import pyautogui
import pytesseract
import cv2
import numpy as np
import pandas as pd
import time
import re
import tkinter as tk
import threading
import argparse
import glob
from PIL import Image
import json
import os
import base64
from dotenv import load_dotenv


# --- 1. Locate the Game Window (Manual Step for Initial Setup) ---
# You'll need to manually determine these coordinates and dimensions once.
# You can use pyautogui.displayMousePosition() or a simple screenshot and image editor.
# For demonstration, let's assume these are the coordinates of the game list area.
# You might need to adjust these significantly based on your screen setup.
GAME_WINDOW_REGION = (
    150,
    300,
    750,
    500,
)  # (left, top, width, height) of the list area
MAX_CAPTURES = 1000  # Maximum number of screenshots to take
ANALYSIS_FOLDER = "analysis"


# --- Helper Functions ---


def preprocess_image_for_ocr(image_path):
    """
    Loads an image, converts it to grayscale, applies thresholding,
    and returns the processed image for better OCR.
    """
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Image not found at {image_path}")

    # --- Advanced Preprocessing Pipeline ---
    # 1. Resize image to make it larger (Tesseract works better on higher DPI images)
    scale_factor = 2
    width = int(img.shape[1] * scale_factor)
    height = int(img.shape[0] * scale_factor)
    img = cv2.resize(img, (width, height), interpolation=cv2.INTER_CUBIC)

    # 2. Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 3. Apply a median blur to reduce salt-and-pepper noise
    blurred = cv2.medianBlur(gray, 3)

    # 4. Use adaptive thresholding
    processed_img = cv2.adaptiveThreshold(
        blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 5
    )

    # 5. Invert the image (Tesseract often performs better on black text on white background)
    processed_img = cv2.bitwise_not(processed_img)

    # Save the processed image for debugging to see what Tesseract is processing
    processed_filename = os.path.join(
        ANALYSIS_FOLDER, "processed_" + os.path.basename(image_path)
    )
    cv2.imwrite(processed_filename, processed_img)
    print(f"  Saved processed image to {processed_filename}")

    return processed_img


def extract_with_gemini(image_paths, resize_factor=1.0):
    """
    Uses Google Gemini to extract names and points from a batch of images.
    Optionally resizes images to reduce cost.
    """
    from google import genai
    from google.genai import types

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print(
            "Error: GEMINI_API_KEY environment variable not set. Please set it to your API key."
        )
        return []

    client = genai.Client(api_key=api_key)

    all_members = []
    chunk_paths = image_paths
    print(f"Processing batch of {len(chunk_paths)} images with Gemini...")

    prompt = """
    Analyze the following screenshots from a game's guild member list.
    For each image, extract the player names and their corresponding points.
    Player names are on the left, and points are numerical values to the right of the name.
    Ignore any text that is not a player name and points pair.
    Return the result as a single JSON object with a key "players" which is a list of objects.
    Each object in the list should have two keys: "Name" (string) and "Points" (integer).
    Example format: {"players": [{"Name": "Player1", "Points": 1500}, {"Name": "Player2", "Points": 1450}]}
    Do not include players with the same name and points multiple times. Members can have 0 points, with the field left empty.
    """
    contents = [prompt]
    for image_path in chunk_paths:
        with open(image_path, "rb") as f:
            img2_bytes = f.read()
            contents.append(
                types.Part.from_bytes(data=img2_bytes, mime_type="image/png")
            )

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash", contents=contents
        )

        cleaned_response = (
            response.text.strip().replace("```json", "").replace("```", "")
        )
        data = json.loads(cleaned_response)
        if "players" in data and isinstance(data["players"], list):
            all_members.extend(data["players"])
            print(f"  Extracted {len(data['players'])} members from this batch.")
        else:
            print("  Warning: Gemini response did not contain a 'players' list.")
    except Exception as e:
        print(f"  An error occurred calling Gemini API or parsing response: {e}")
        print(f"  Raw response was: {response.text}")

    return all_members


# --- GUI and Stop Flag ---
stop_capture_flag = False


def create_stop_button():
    """Creates and runs a Tkinter window with a stop button."""
    global stop_capture_flag

    def on_stop_click():
        """Sets the stop flag and closes the GUI window."""
        global stop_capture_flag
        stop_capture_flag = True
        root.destroy()

    root = tk.Tk()
    root.title("Capture Control")
    root.geometry("150x60")
    root.attributes("-topmost", True)  # Keep window on top

    stop_button = tk.Button(root, text="Stop Capture", command=on_stop_click)
    stop_button.pack(pady=15, padx=15, fill=tk.BOTH, expand=True)

    # Also stop if the user closes the window
    root.protocol("WM_DELETE_WINDOW", on_stop_click)
    root.mainloop()


def extract_names_and_points(text):
    """
    Parses the OCR'd text to extract names and points.
    This regex needs to be robust for various OCR errors.
    """
    names_points = []
    # Regex to find a word (name) followed by numbers (points)
    # It tries to be flexible with common OCR mistakes (e.g., 'O' instead of '0')
    # This pattern assumes names are typically alphanumeric and points are numbers.
    # It also accounts for potential extra characters or spaces between.
    pattern = r"([A-Za-z0-9_ -]+)\s*(\d{3,5})"  # Name (letters, numbers, underscore, space, hyphen), then 3-5 digits (points)

    lines = text.split("\n")
    for line in lines:
        line = line.strip()
        if not line:
            continue

        match = re.search(pattern, line)
        if match:
            name = match.group(1).strip()
            points = match.group(2).strip()
            # Basic cleaning for names (remove common OCR artifacts)
            name = re.sub(r"[^A-Za-z0-9_ ]", "", name).strip()
            names_points.append({"Name": name, "Points": int(points)})
            # print(f"  Found: Name='{name}', Points='{points}'")
    return names_points


# --- Main Script ---
if __name__ == "__main__":
    # Load environment variables from .env file if available
    if load_dotenv:
        load_dotenv()

    parser = argparse.ArgumentParser(
        description="Extract guild member data from screenshots."
    )
    parser.add_argument(
        "--analyze-only",
        action="store_true",
        help="Skip capture phase and only analyze existing guild_screenshot_*.png files.",
    )

    parser.add_argument(
        "--gemini-resize-factor",
        type=float,
        default=1.0,
        help="Factor to resize images before sending to Gemini (e.g., 0.75 for 75%% size). Default is 1.0 (no resize).",
    )
    parser.add_argument(
        "--screenshot-only",
        action="store_true",
        help="Only perform the screenshot capture phase and then exit.",
    )
    args = parser.parse_args()

    if args.analyze_only and args.screenshot_only:
        print("Error: --analyze-only and --screenshot-only cannot be used together.")
        exit()

    # Create analysis folder if it doesn't exist
    os.makedirs(ANALYSIS_FOLDER, exist_ok=True)
    os.makedirs("Results", exist_ok=True)

    all_guild_members_data = []
    seen_members = set()  # To prevent duplicate entries during scrolling
    screenshot_files = []

    if not args.analyze_only:
        consecutive_same_captures = 0
        previous_screenshot = None

        print("Starting automated guild data extraction...")
        print(
            "Ensure the game window is visible and positioned within the GAME_WINDOW_REGION."
        )
        print("You have 5 seconds to switch to the game window.")
        print("The script will take screenshots every second. Please scroll manually.")
        print("A 'Stop Capture' button will appear. Click it to stop manually.")
        print("Capturing will also stop after 3 consecutive identical screenshots.")

        # Start the GUI in a separate thread
        gui_thread = threading.Thread(target=create_stop_button, daemon=True)
        gui_thread.start()

        time.sleep(3)  # Give user time to switch to the game window

        # --- Capture Phase ---
        print("\n--- Starting Capture Phase ---")
        for i in range(MAX_CAPTURES):
            screenshot_filename = os.path.join(
                ANALYSIS_FOLDER, f"guild_screenshot_{i}.png"
            )

            try:
                # Check for manual stop signal
                if stop_capture_flag:
                    print("Manual stop detected. Stopping capture.")
                    break

                # Take and save screenshot
                print(f"Taking screenshot {i+1}...")
                current_screenshot = pyautogui.screenshot(region=GAME_WINDOW_REGION)
                current_screenshot.save(screenshot_filename)
                screenshot_files.append(screenshot_filename)

                # Compare with previous screenshot to detect end of scrolling
                if previous_screenshot is not None:
                    # Convert to numpy arrays for comparison
                    current_np = np.array(current_screenshot)
                    previous_np = np.array(previous_screenshot)
                    if np.array_equal(current_np, previous_np):
                        consecutive_same_captures += 1
                        print(
                            f"  Identical screenshot detected ({consecutive_same_captures}/2)."
                        )
                    else:
                        consecutive_same_captures = 0  # Reset counter

                previous_screenshot = current_screenshot

                if (
                    consecutive_same_captures >= 2
                ):  # 2 means 3 identical frames in a row
                    print(
                        "Three consecutive identical captures detected. Stopping capture."
                    )
                    break

                time.sleep(0.75)  # Wait for user to scroll

            except pyautogui.PyAutoGUIException as e:
                print(f"PyAutoGUI error during capture: {e}. Stopping.")
                break
            except Exception as e:
                print(f"An error occurred during capture: {e}. Stopping.")
                break

        print(
            f"\n--- Capture Phase Finished. Collected {len(screenshot_files)} screenshots. ---"
        )
        if args.screenshot_only:
            print("Screenshot-only mode enabled. Exiting without analysis.")
            exit()
    else:
        # --- Find existing files for analysis ---
        print("\n--- Analyze-Only Mode: Searching for existing screenshots ---")
        screenshot_files = sorted(
            glob.glob(os.path.join(ANALYSIS_FOLDER, "guild_screenshot_*.png"))
        )
        if not screenshot_files:
            print(
                f"No 'guild_screenshot_*.png' files found in the '{ANALYSIS_FOLDER}' directory. Exiting."
            )
        else:
            print(f"Found {len(screenshot_files)} files to analyze.")

    # --- Analysis Phase ---
    if screenshot_files:
        print("\n--- Starting Analysis Phase ---")
        # --- Gemini AI Pipeline (processes all images in one go) ---
        all_guild_members_data = extract_with_gemini(
            screenshot_files, resize_factor=args.gemini_resize_factor
        )

    # 6. Create DataFrame and Export to Excel
    if all_guild_members_data:
        # Remove duplicates based on Name and Points if any managed to sneak through
        # Using a DataFrame's drop_duplicates is robust
        df = (
            pd.DataFrame(all_guild_members_data)
            .drop_duplicates(subset=["Name", "Points"])
            .reset_index(drop=True)
        )
        excel_filename = os.path.join("Results", "guild_members.xlsx")
        df.to_excel(excel_filename, index=False)
        print(
            f"\nSuccessfully extracted {len(df)} unique guild members to {excel_filename}"
        )
        print("Data preview:")
        print(df.head())
