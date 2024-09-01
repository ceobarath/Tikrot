import os
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
from tqdm import tqdm

def process_video(input_path, output_folder):
    # Ensure output folder exists
    os.makedirs(output_folder, exist_ok=True)
    
    # Generate output path
    output_path = os.path.join(output_folder, os.path.basename(input_path))
    
    # Load video
    video = VideoFileClip(input_path)
    
    # Create caption
    caption_text = "YOUR CAPTION TEXT".upper()
    caption = TextClip(caption_text, fontsize=50, color='white', font='Arial-Bold', stroke_color='black', stroke_width=2)
    caption = caption.set_position(('center', 'center')).set_duration(video.duration)
    
    # Compose video with caption
    final_video = CompositeVideoClip([video, caption])
    
    # Write output video with progress bar
    total_frames = int(final_video.duration * final_video.fps)
    with tqdm(total=total_frames, unit='frames', desc=f"Processing {os.path.basename(input_path)}") as pbar:
        final_video.write_videofile(output_path, codec='libx264', audio_codec='aac', 
                                    progress_callback=lambda *args: pbar.update(1))
    
    # Close video objects
    video.close()
    final_video.close()

# Process all videos in input folder
input_folder = "input_videos"
output_folder = "output_videos"

for video_file in os.listdir(input_folder):
    if video_file.endswith(('.mp4', '.avi', '.mov')):  # Add more extensions if needed
        input_path = os.path.join(input_folder, video_file)
        process_video(input_path, output_folder)

print("All videos processed successfully!")