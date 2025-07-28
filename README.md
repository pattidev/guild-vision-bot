# Guild Data Extraction System

An AI-powered computer vision solution that automates the extraction of guild member data from mobile game interfaces, eliminating hours of manual data entry and achieving >99% accuracy through intelligent image processing.

## 🎯 Project Overview

This project solves a common data collection problem: extracting structured information from applications that don't provide APIs. Using computer vision and Google Gemini AI, it automatically captures and processes guild member data from mobile game screenshots, transforming 3+ hours of weekly manual transcription into 10 minutes of automated processing.

**Read the complete case study**: [AI-Powered Data Collection: Building APIs Where None Exist (Part 2)](BLOG_POST_PART2.md)

## 🚀 Key Features

- **Automated Screenshot Capture**: Programmatically captures screenshots while user scrolls through game interface
- **AI-Powered Data Extraction**: Uses Google Gemini to intelligently extract player names and points from images
- **Smart Duplicate Detection**: Automatically identifies and removes duplicate entries from overlapping screenshots
- **Multiple OCR Engines**: Supports Tesseract, Surya OCR, and Gemini AI for different use cases
- **Cost Optimization**: Optional image resizing to reduce API costs while maintaining accuracy
- **User-Friendly Interface**: Clean GUI with real-time feedback and manual stop controls
- **Robust Error Handling**: Continues processing even if individual images fail
- **Professional Output**: Exports to Excel format ready for business integration

## 📋 Requirements

### System Dependencies
- Python 3.8+
- Windows with Phone Link (for Android screen mirroring)
- Tesseract OCR (optional, for traditional OCR)

### Python Dependencies
```bash
pip install -r requirements.txt
```

Core packages:
- `google-generativeai` - Google Gemini AI integration
- `pyautogui` - Screenshot automation
- `opencv-python` - Image preprocessing
- `pandas` - Data processing and Excel export
- `pillow` - Image handling
- `python-dotenv` - Environment variable management
- `tkinter` - GUI interface (usually included with Python)

## 🛠️ Installation & Setup

### 1. Clone Repository
```bash
git clone <repository-url>
cd guildsheetupdate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure API Key
Create a `.env` file in the project root:
```env
GEMINI_API_KEY=your_google_gemini_api_key_here
```

### 4. Configure Screen Region
Update `GAME_WINDOW_REGION` in `main.py` to match your screen setup:
```python
GAME_WINDOW_REGION = (
    150,    # left
    300,    # top  
    750,    # width
    500,    # height
)
```

Use `pyautogui.displayMousePosition()` to find coordinates.

## 🎮 Usage

### Basic Usage (Full Pipeline)
```bash
# Capture screenshots + AI analysis + Excel export
python main.py
```

### Screenshot Only
```bash
# Just capture screenshots without processing
python main.py --screenshot-only
```

### Analysis Only
```bash
# Process existing screenshots in analysis/ folder
python main.py --analyze-only
```

### Cost Optimization
```bash
# Resize images to 75% before sending to Gemini (reduces costs)
python main.py --gemini-resize-factor 0.75
```

### Alternative OCR Engines
```bash
# Use traditional Tesseract OCR instead of Gemini
python main.py --use-tesseract

# Use Surya OCR (requires: pip install surya-ocr)
python main.py --use-surya
```

## 📁 Project Structure

```
guildsheetupdate/
├── main.py                 # Main application script
├── analysis/              # Screenshots and processed images
│   ├── guild_screenshot_*.png
│   ├── processed_*.png    # Tesseract preprocessing
│   └── *_detection.json   # Surya OCR debug data
├── Results/               # Output Excel files
│   └── guild_members.xlsx
├── .env                   # API keys (create this)
├── requirements.txt       # Python dependencies
├── README.md             # This file
└── BLOG_POST_PART2.md    # Complete technical case study
```

## 🧠 Technical Architecture

### Computer Vision Pipeline
1. **Screen Mirroring**: Android game → Windows Phone Link
2. **Automated Capture**: PyAutoGUI screenshots with smart stopping detection
3. **Image Preprocessing**: OpenCV optimization for text recognition
4. **AI Extraction**: Google Gemini multimodal processing
5. **Data Processing**: Pandas deduplication and Excel export

### Why AI Over Traditional OCR

Through development iterations, we discovered that Google Gemini significantly outperforms traditional OCR approaches:

| Feature | Traditional OCR | Gemini AI |
|---------|----------------|-----------|
| Accuracy | ~85% | >99% |
| Setup Complexity | High (regex patterns) | Low (single prompt) |
| Maintenance | Ongoing updates | Zero maintenance |
| Edge Cases | Poor handling | Excellent |
| Context Understanding | None | Advanced |

### Development Evolution

This project went through several iterations during development:

1. **Initial Approach**: Traditional Tesseract OCR with complex regex patterns
2. **Surya Integration**: Attempted modern OCR with better accuracy
3. **Gemini Discovery**: Found AI dramatically outperformed deterministic approaches
4. **Architecture Refinement**: Added batching, resizing, and error handling
5. **User Experience**: Added GUI, file organization, and multiple operation modes

## ⚙️ Configuration Options

### Command Line Arguments
- `--analyze-only`: Skip capture, process existing screenshots
- `--screenshot-only`: Capture screenshots without processing
- `--use-tesseract`: Use Tesseract OCR instead of Gemini
- `--gemini-resize-factor`: Resize images before Gemini processing (0.1-1.0)

### Environment Variables
- `GEMINI_API_KEY`: Google Gemini API key (required for AI processing)

### Constants (in main.py)
- `GAME_WINDOW_REGION`: Screenshot capture area
- `MAX_CAPTURES`: Maximum screenshots to take (default: 1000)
- `ANALYSIS_FOLDER`: Directory for screenshots and debug files

### Performance Optimization

**Reduce API Costs**:
```bash
python main.py --gemini-resize-factor 0.5
```

**Faster Processing**:
- Use smaller capture regions
- Process fewer screenshots with `--analyze-only`
- Consider Tesseract for simple interfaces

## 🎯 Business Impact

### Quantified Results
- **94% time reduction**: 3+ hours → 10 minutes weekly
- **>99% accuracy**: Eliminated human transcription errors
- **100% automation**: No manual data entry required
- **Transferable process**: Any administrator can operate

### Use Cases Beyond Gaming
- Legacy system integration without APIs
- Compliance monitoring from visual dashboards  
- Competitive analysis from public interfaces
- Document processing from PDF-based workflows

## 🤝 Contributing

This project demonstrates practical AI integration patterns and computer vision techniques. Contributions welcome for:

- Additional OCR engine integrations
- Mobile platform support (iOS)
- Batch processing optimizations
- Alternative AI model support
- UI/UX improvements

## 📄 License
Apache License 2.0

## 🔗 Related Projects

This is Part 2 of a complete automation solution:
- **Part 1**: [Serverless Discord Economy Bot](docs/BLOG_POST.md)
- **Portfolio**: [Complete Case Study](docs/PORTFOLIO_CASE_STUDY.md)

The complete system demonstrates modern automation architecture combining serverless computing, AI integration, and user-centered design.

---

*Built with ❤️ to eliminate tedious work and empower human creativity*
```