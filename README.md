# 🌍 Multilingual Text-to-Speech Translator

A complete web application that automatically detects the language of input text, translates it to a target language, and converts the translated text into natural-sounding speech audio.

## 📋 Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [How to Run](#how-to-run)
- [How It Works](#how-it-works)
- [Usage Examples](#usage-examples)
- [Technical Details](#technical-details)
- [Troubleshooting](#troubleshooting)

## ✨ Features

- 🔍 **Automatic Language Detection**: Detects the source language of input text automatically
- 🌐 **Text Translation**: Translates text to 100+ languages using Google Translate
- 🔊 **Text-to-Speech**: Converts translated text into high-quality speech audio
- 💾 **Audio Export**: Saves all generated audio files with unique timestamps (no overwriting)
- 🎵 **Browser Playback**: Plays audio directly in the web browser
- 📱 **User-Friendly UI**: Clean and intuitive Streamlit interface
- 📄 **Multiple File Formats**: Supports text input, file upload (.txt, .pdf, .doc, .docx)
- 🎯 **Multiple Languages**: Supports all 12 major Indian languages plus 100+ more languages
- 📁 **File Management**: All generated audio files are preserved with unique filenames

## 📁 Project Structure

```
TextToSpeech/
│
├── app/
│   └── app.py                    # Main Streamlit application (UI)
│
├── services/
│   ├── translation_service.py   # Language detection and translation service
│   └── speech_service.py        # Text-to-speech conversion service
│
├── output/
│   └── speech_*.mp3             # Generated audio files with unique timestamps (created at runtime)
│
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## 🚀 Installation

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)
- Internet connection (required for translation and TTS services)

### Step-by-Step Installation

1. **Clone or navigate to the project directory**
   ```bash
   cd "TextToSpeech"
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # Linux/Mac
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install required dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Verify installation**
   ```bash
   python -c "import streamlit; import deep_translator; import langdetect; import gtts; print('All dependencies installed successfully!')"
   ```

## ▶️ How to Run

### Starting the Application

1. **Activate your virtual environment** (if using one)
   ```bash
   # Windows
   venv\Scripts\activate

   # Linux/Mac
   source venv/bin/activate
   ```

2. **Run the Streamlit application**
   ```bash
   streamlit run app/app.py
   ```

3. **Open in browser**
   - The application will automatically open in your default browser
   - If not, navigate to: `http://localhost:8501`

### Using the Application

1. **Enter Text or Upload File**: 
   - **Type Text**: Type or paste your text in the text input area (any language)
   - **Upload File**: Upload a text file (.txt), PDF (.pdf), or Word document (.doc/.docx)
2. **Select Target Language**: Choose your target language from the dropdown menu (12 Indian languages + 100+ more)
3. **Generate Speech**: Click the "Generate Speech" button
4. **View Results**: 
   - See detected source language
   - View translated text
   - Listen to audio playback
   - Download MP3 file (with unique filename)
   - All generated files are saved in `/output` folder with timestamps

## 🔧 How It Works

### Internal System Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    User Input (Text)                         │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 1: Language Detection                                  │
│  ───────────────────────────────                            │
│  translation_service.detect_language(text)                  │
│  • Uses langdetect library                                   │
│  • Returns: language code, name, confidence                  │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 2: Text Translation                                    │
│  ───────────────────────────────                            │
│  translation_service.translate_text(text, target_lang)      │
│  • Uses deep-translator library (GoogleTranslator)           │
│  • Translates from detected language to target language     │
│  • Returns: translated text, source/target language codes   │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 3: Text-to-Speech Conversion                          │
│  ───────────────────────────────                            │
│  speech_service.text_to_speech(text, lang_code, filename)   │
│  • Uses gTTS (Google Text-to-Speech) library                │
│  • Generates natural-sounding speech audio                   │
│  • Saves as MP3 file with unique timestamp in /output folder│
│  • Format: speech_{lang_code}_{timestamp}.mp3              │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 4: Audio Playback & Download                          │
│  ───────────────────────────────                            │
│  • Streamlit audio player displays audio                    │
│  • User can play audio directly in browser                   │
│  • Download button available for MP3 file                    │
└─────────────────────────────────────────────────────────────┘
```

### Code Architecture

#### 1. **Translation Service** (`services/translation_service.py`)

**Purpose**: Handles language detection and text translation

**Key Methods**:
- `detect_language(text)`: Detects the language of input text
  - Returns: Language code, name, and confidence score
- `translate_text(text, target_lang_code)`: Translates text to target language
  - Returns: Translated text, source/target language codes

**Libraries Used**: 
- `langdetect` - Language detection library
- `deep-translator` - Google Translate API wrapper (Python 3.13 compatible)

#### 2. **Speech Service** (`services/speech_service.py`)

**Purpose**: Handles text-to-speech conversion

**Key Methods**:
- `text_to_speech(text, lang_code, filename)`: Converts text to speech
  - Creates MP3 audio file
  - Saves to `/output` directory
  - Returns: File path and success status

**Library Used**: `gTTS` - Google Text-to-Speech API wrapper

#### 3. **Streamlit App** (`app/app.py`)

**Purpose**: Provides web user interface

**Key Components**:
- Text input area OR file upload option (.txt, .pdf, .doc, .docx)
- Language dropdown for target language selection (12 Indian languages + 100+ more)
- Generate Speech button
- Results display:
  - Detected language information
  - Original and translated text
  - Audio player with download option
  - Unique filename for each generation

**Libraries Used**: 
- `streamlit` - Web application framework
- `PyPDF2` - PDF text extraction
- `python-docx` - Word document text extraction

## 📝 Usage Examples

### Example 1: English to Telugu

**Input:**
```
Text: "Hello, how are you?"
Target Language: Telugu
```

**Process:**
1. Detects: English (en)
2. Translates: "నమస్కారం, మీరు ఎలా ఉన్నారు?"
3. Generates: Telugu speech audio
4. Saves: `output/speech_te_20250111_143022.mp3` (unique timestamp)
5. Plays: Audio in browser

### Example 2: Hindi to English

**Input:**
```
Text: "नमस्ते, आप कैसे हैं?"
Target Language: English
```

**Process:**
1. Detects: Hindi (hi)
2. Translates: "Hello, how are you?"
3. Generates: English speech audio
4. Saves: `output/speech_en_20250111_143045.mp3` (unique timestamp)
5. Plays: Audio in browser

### Example 3: Spanish to Tamil

**Input:**
```
Text: "Hola, ¿cómo estás?"
Target Language: Tamil
```

**Process:**
1. Detects: Spanish (es)
2. Translates: "வணக்கம், நீங்கள் எப்படி இருக்கிறீர்கள்?"
3. Generates: Tamil speech audio
4. Saves: `output/speech_ta_20250111_143110.mp3` (unique timestamp)
5. Plays: Audio in browser

### Example 4: Upload PDF File

**Input:**
```
File: document.pdf (contains text in any language)
Target Language: Hindi
```

**Process:**
1. Extracts text from PDF (all pages)
2. Detects source language automatically
3. Translates to Hindi
4. Generates: Hindi speech audio
5. Saves: `output/speech_hi_20250111_143125.mp3`
6. Plays: Audio in browser

## 🔍 Technical Details

### Dependencies

| Library | Version | Purpose |
|---------|---------|---------|
| `streamlit` | >=1.39.0 | Web UI framework |
| `deep-translator` | 1.11.4 | Text translation (Python 3.13 compatible) |
| `langdetect` | 1.0.9 | Language detection (Python 3.13 compatible) |
| `gTTS` | 2.5.0 | Text-to-speech conversion |
| `PyPDF2` | 3.0.1 | PDF text extraction |
| `python-docx` | 1.1.0 | Word document text extraction |

### Supported Languages

The application supports 100+ languages including:

- **Indian Languages (12 major languages)**: 
  - Hindi, Urdu, Assamese, Bengali, Gujarati, Kannada, Malayalam, Marathi, Odia, Punjabi, Tamil, Telugu
- **European Languages**: Spanish, French, German, Italian, Portuguese, Russian
- **Asian Languages**: Japanese, Korean, Chinese, Arabic, Nepali, Sinhala
- **Other Languages**: English and 100+ more languages

### File Output

- **Output File Format**: `speech_{language_code}_{timestamp}.mp3`
- **Example**: `speech_te_20250111_143022.mp3`
- **Location**: `/output` folder in project root
- **Behavior**: Each generation creates a new file with unique timestamp (no overwriting)
- **Format**: MP3 audio format
- **File Management**: All generated audio files are preserved

### Supported File Upload Formats

- **Text Files**: `.txt` (UTF-8 encoding)
- **PDF Documents**: `.pdf` (text extraction from all pages)
- **Word Documents**: `.doc`, `.docx` (paragraph text extraction)
- **Preview**: Shows first 1000 characters of uploaded file content

### API Services Used

1. **Google Translate API** (via deep-translator)
   - Text translation
   - Supports 100+ languages
   - Python 3.13 compatible
   - Requires internet connection

2. **Language Detection** (via langdetect)
   - Automatic language detection
   - Python 3.13 compatible
   - No API key required

3. **Google Text-to-Speech API** (via gTTS)
   - Speech synthesis
   - Natural-sounding voices
   - Requires internet connection

## 🐛 Troubleshooting

### Common Issues and Solutions

#### 1. **ModuleNotFoundError**
```
Error: No module named 'streamlit'
```

**Solution:**
```bash
pip install -r requirements.txt
```

#### 2. **Audio Not Playing**
- Check if audio file exists in `/output` folder
- Verify internet connection (required for TTS)
- Try refreshing the browser page
- Check browser console for errors

#### 2a. **PDF/DOCX File Upload Issues**
```
Error: No module named 'PyPDF2' or 'docx'
```

**Solution:**
```bash
pip install PyPDF2 python-docx
```

#### 3. **Translation Failed**
- Check internet connection
- Verify language code is valid
- Try with shorter text

#### 4. **Port Already in Use**
```
Error: Port 8501 is already in use
```

**Solution:**
- Stop other Streamlit instances
- Or use different port: `streamlit run app/app.py --server.port 8502`

#### 5. **File Permission Error**
- Ensure `/output` folder exists and is writable
- Check file permissions on Windows/Mac/Linux

#### 6. **Import Errors**
```
Error: cannot import name 'TranslationService'
```

**Solution:**
- Ensure you're running from project root: `streamlit run app/app.py`
- Check that all files are in correct directories

## 📚 Additional Information

### Code Quality

- ✅ Clean, readable Python code
- ✅ Comprehensive comments explaining each step
- ✅ Error handling implemented
- ✅ Modular architecture (services separated)
- ✅ User-friendly error messages

### Performance Notes

- Translation and TTS require internet connection
- Processing time depends on:
  - Text length
  - Internet speed
  - Google API response time
- Audio files are typically generated within 2-5 seconds

### Security & Privacy

- Text is sent to Google Translate and TTS services
- No data is stored permanently (except generated MP3 files)
- Use for non-sensitive content

## 🚀 Recent Updates

### Version 2.1 Features (Natural Voice Enhancement):
- ✅ **HD Natural Voice Quality**: Now using OpenAI's `tts-1-hd` model by default for the most natural-sounding voices
- ✅ **Voice Quality Selection**: Choose between HD (Natural) or Standard quality models
- ✅ **Enhanced Voice Descriptions**: Improved voice descriptions to help select the most natural-sounding options
- ✅ **Reference Voice Comparison**: Upload reference voice files to compare with generated voices (for comparison only, not cloning)
- ✅ **Better Voice Matching**: Optimized voice selection for natural-sounding speech similar to professional recordings

### Version 2.0 Features:
- ✅ **Unique File Management**: All generated audio files are saved with unique timestamps (no overwriting)
- ✅ **Multi-Format Support**: Upload text files (.txt), PDFs (.pdf), and Word documents (.doc/.docx)
- ✅ **12 Indian Languages**: Complete support for all major Indian languages including Assamese and Odia
- ✅ **Python 3.13 Compatible**: Updated to use deep-translator and langdetect (no cgi module dependency)
- ✅ **Enhanced File Preview**: Shows file content preview with character count
- ✅ **Improved UI**: Cleaner interface without sidebar

## 🤝 Contributing

Feel free to enhance this project by:
- Adding more language support
- Improving UI/UX
- Adding batch processing
- Implementing voice selection
- Adding speech speed control
- Adding audio format options (WAV, OGG)

## 📄 License

This project is open source and available for educational and personal use.

## 🙏 Acknowledgments

- **deep-translator**: For language translation (Python 3.13 compatible)
- **langdetect**: For language detection
- **gTTS**: For text-to-speech conversion
- **PyPDF2**: For PDF text extraction
- **python-docx**: For Word document text extraction
- **Streamlit**: For the web application framework

---

**Made with ❤️ for multilingual communication**

**Happy Translating and Speaking! 🎉**
