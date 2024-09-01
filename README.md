# TikRot - TikTok Content Generator

TikRot is a Streamlit application that automates the creation of TikTok-style videos from PDF content.

## Features

- PDF text extraction
- Script generation using OpenAI's GPT
- Text-to-speech audio generation
- Video processing with subtitles
- Project saving and loading

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/tikrot.git
   cd tikrot
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up your OpenAI API key as an environment variable:
   ```
   export OPENAI_API_KEY='your-api-key-here'
   ```

## Usage

1. Run the Streamlit app:
   ```
   streamlit run streamlit_app.py
   ```

2. Open the provided URL in your web browser.

3. Log in using the mock credentials (replace with actual authentication in production).

4. Upload a PDF file and click "Generate TikTok" to create videos.

5. View generated videos, save projects, and manage your project history.

## Requirements

- Python 3.7+
- Streamlit
- OpenAI API access
- FFmpeg (for video processing)

## Note

Ensure you have template videos in the `template_videos` folder for the app to use in video generation.

## License


