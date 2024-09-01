import streamlit as st
import requests
import base64
import io
import tempfile
import os
from datetime import datetime
import pandas as pd
from openai import OpenAI
import cv2
import numpy as np
from pydub import AudioSegment
import random
from pathlib import Path
import PyPDF2
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeVideoClip, TextClip, ColorClip
from moviepy.video.tools.subtitles import SubtitlesClip

# Initialize the OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Mock user database (replace with actual database in production)
USERS = {
    "user1": "password1",
    "user2": "password2"
}

# Available voices
VOICES = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]

# Authentication functions
def login():
    st.sidebar.title("Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        if username in USERS and USERS[username] == password:
            st.session_state.user = username
            st.success(f"Logged in as {username}")
            st.rerun()
        else:
            st.error("Invalid username or password")

def logout():
    st.sidebar.title("User: " + st.session_state.user)
    if st.sidebar.button("Logout"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# Project management functions
def save_project(project_name, scripts, audio_files, video_files):
    if 'projects' not in st.session_state:
        st.session_state.projects = []

    project = {
        'name': project_name,
        'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'scripts': scripts,
        'audio_files': audio_files,
        'video_files': video_files
    }
    st.session_state.projects.append(project)

def load_project(project):
    st.session_state.scripts = project['scripts']
    st.session_state.audio_files = project['audio_files']
    st.session_state.video_files = project['video_files']

# UI Components
def sidebar():
    with st.sidebar:
        if 'user' in st.session_state:
            logout()
        else:
            login()

def project_history():
    st.title("Project History")
    if 'projects' in st.session_state and st.session_state.projects:
        for i, project in enumerate(st.session_state.projects):
            with st.expander(f"{project['name']} - {project['date']}"):
                st.write(f"Scripts: {len(project['scripts'])}")
                if st.button("Load Project", key=f"load_{i}"):
                    load_project(project)

# PDF processing and script generation
def generate_scripts(pdf_content):
    prompt = f"Generate 3 TikTok scripts based on the following content. Each script should have a main content and a call-to-action:\n\n{pdf_content}\n\nProvide the output in the following format for each script:\nScript [number]:\nMain Content: [main content]\nCall-to-Action: [call-to-action]"

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a creative TikTok script writer."},
            {"role": "user", "content": prompt}
        ]
    )

    raw_scripts = response.choices[0].message.content.split("Script ")[1:]
    scripts = []
    for script in raw_scripts:
        parts = script.split("Call-to-Action:")
        content = parts[0].split("Main Content:")[1].strip()
        call_to_action = parts[1].strip()
        scripts.append({"content": content, "call_to_action": call_to_action})
    return scripts

# Audio generation using OpenAI TTS
def generate_audio(text, voice):
    response = client.audio.speech.create(
        model="tts-1",
        voice=voice,
        input=text
    )
    return response.content

# Extract text from PDF
def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

# Generate subtitles with Whisper
def generate_subtitles_with_whisper(audio_path):
    print('Generating subtitles with Whisper API')

    with open(audio_path, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1", 
            file=audio_file,
            response_format="srt"
        )

    return parse_srt(transcript)

def parse_srt(srt_string):
    lines = srt_string.strip().split('\n\n')
    text_array = []
    for line in lines:
        parts = line.split('\n')
        if len(parts) >= 3:
            time_range = parts[1].split(' --> ')
            start_time = time_to_seconds(time_range[0])
            end_time = time_to_seconds(time_range[1])
            text = ' '.join(parts[2:])
            text_array.append([text, start_time, end_time])
    return text_array

def time_to_seconds(time_str):
    h, m, s = time_str.split(':')
    return int(h) * 3600 + int(m) * 60 + float(s.replace(',', '.'))

# Video processing with improved caption synchronization and 1080p output
def process_video(video_path, audio_path, subtitles, output_path):
    # Ensure we have a valid output path
    if not output_path:
        output_path = os.path.join(os.getcwd(), "output_videos", "processed_video.mp4")
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Load video
    video = VideoFileClip(video_path)
    
    # Crop video to 9:16 aspect ratio
    aspect_ratio = 9/16
    if video.w / video.h > aspect_ratio:
        crop_width = video.h * aspect_ratio
        x_center = video.w / 2
        video = video.crop(x1=x_center - crop_width/2, y1=0, x2=x_center + crop_width/2, y2=video.h)
    else:
        crop_height = video.w / aspect_ratio
        y_center = video.h / 2
        video = video.crop(x1=0, y1=y_center - crop_height/2, x2=video.w, y2=y_center + crop_height/2)
    
    # Resize to 1080p (1080x1920)
    video = video.resize(height=1920)
    
    # Load audio and set video duration
    audio = AudioFileClip(audio_path)
    video = video.subclip(0, audio.duration)
    
    def create_textclip(txt):
        # Split text into words
        words = txt.split()
        clips = []
        
        for i in range(0, len(words), 3):
            line = ' '.join(words[i:i+3])
            text_clip = TextClip(
                line.upper(),
                font="Arial-Bold",
                fontsize=80,
                color='yellow',
                stroke_color='black',
                stroke_width=2,
                method='label',
                size=(video.w * 0.9, None)
            )
            text_clip = text_clip.set_position(('center', 'center'))
            clips.append(text_clip)
        
        return clips

    # Convert subtitles to the format expected by CompositeVideoClip
    subtitle_clips = []
    for text, start, end in subtitles:
        clips = create_textclip(text)
        duration = (end - start) / len(clips)
        for i, clip in enumerate(clips):
            subtitle_clips.append(clip.set_start(start + i * duration).set_duration(duration))

    # Composite video with subtitles
    final_video = CompositeVideoClip([video] + subtitle_clips)
    
    # Set audio
    final_video = final_video.set_audio(audio)
    
    # Write final video
    final_video.write_videofile(output_path, codec="libx264", audio_codec="aac", fps=30)
    
    return output_path

# Main app logic
def main():
    sidebar()
    
    if 'user' not in st.session_state:
        st.title("Welcome to TikRot v2")
        st.write("Please login to continue.")
        return

    st.title("TikRot - Brain Rot Automation!")

    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    if uploaded_file is not None:
        if st.button("Generate TikTok"):
            with st.spinner("Generating TikTok content..."):
                # Step 1: Extract text from PDF
                st.text("Extracting text from PDF...")
                pdf_content = extract_text_from_pdf(uploaded_file)

                # Step 2: Generate scripts
                st.text("Generating scripts...")
                scripts = generate_scripts(pdf_content)
                st.session_state.scripts = scripts

                # Step 3: Generate audio for each script with random voices
                st.text("Generating audio...")
                audio_files = []
                used_voices = []
                for script in scripts:
                    voice = random.choice(VOICES)
                    used_voices.append(voice)
                    audio = generate_audio(script['content'] + " " + script['call_to_action'], voice)
                    audio_files.append(audio)
                st.session_state.audio_files = audio_files

                # Step 4: Generate subtitles and process videos
                st.text("Generating subtitles and processing videos...")
                template_folder = Path("template_videos")
                template_videos = list(template_folder.glob("*.mp4"))
                if not template_videos:
                    st.error("No template videos found. Please add some videos to the 'template_videos' folder.")
                    return

                final_videos = []
                progress_bar = st.progress(0)
                stop_button = st.button("Stop Processing")
                for i, audio in enumerate(audio_files):
                    if stop_button:
                        st.warning("Video processing stopped by user.")
                        break
                    
                    st.text(f"Processing video {i+1}/{len(audio_files)}...")
                    audio_path = f"temp_audio_{i}.mp3"
                    with open(audio_path, "wb") as f:
                        f.write(audio)

                    subtitles = generate_subtitles_with_whisper(audio_path)
                    
                    video_path = str(random.choice(template_videos))
                    output_video_path = os.path.join("output_videos", f"final_video_{i}.mp4")
                    
                    # Create a placeholder for video processing progress
                    video_progress = st.empty()
                    def progress_callback(t):
                        video_progress.text(f"Exporting video {i+1}: {t:.1f}%")
                    
                    processed_video = process_video(video_path, audio_path, subtitles, output_video_path)
                    final_videos.append((processed_video, subtitles, used_voices[i]))
                    
                    # Update overall progress
                    progress_bar.progress((i + 1) / len(audio_files))

                st.session_state.final_videos = final_videos

                if not stop_button:
                    st.success("TikTok content generated successfully!")
                else:
                    st.info(f"Processing stopped. {len(final_videos)} videos were completed.")

    if 'final_videos' in st.session_state:
        for i, (video_path, subtitles, voice) in enumerate(st.session_state.final_videos):
            st.subheader(f"Video {i+1}")
            st.video(video_path)
            st.text(f"Voice used: {voice}")
            st.text("Subtitles:")
            st.write(subtitles)

        project_name = st.text_input("Project Name")
        if st.button("Save Project"):
            save_project(project_name, st.session_state.scripts, st.session_state.audio_files, st.session_state.final_videos)
            st.success("Project saved successfully!")

    project_history()

if __name__ == "__main__":
    main()