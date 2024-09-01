from moviepy.editor import VideoFileClip, AudioFileClip, CompositeVideoClip, TextClip
from moviepy.video.fx.all import crop, resize

def process_video(video_path, audio_path, output_path, subtitles):
    video = VideoFileClip(video_path)
    audio = AudioFileClip(audio_path)
    
    # Crop video to 9:16 aspect ratio
    aspect_ratio = 9/16
    if video.w / video.h > aspect_ratio:
        new_w = int(video.h * aspect_ratio)
        video = crop(video, width=new_w, height=video.h, x_center=video.w/2, y_center=video.h/2)
    else:
        new_h = int(video.w / aspect_ratio)
        video = crop(video, width=video.w, height=new_h, x_center=video.w/2, y_center=video.h/2)
    
    # Resize to standard TikTok size
    video = resize(video, width=1080)
    
    # Set video duration to match audio duration
    video = video.subclip(0, audio.duration)
    
    # Add subtitles
    subtitle_clips = [
        TextClip(txt, fontsize=24, color='white', bg_color='black', size=(video.w, None))
        .set_position(('center', 'bottom'))
        .set_duration(end - start)
        .set_start(start)
        for (start, end, txt) in subtitles
    ]
    
    # Combine video, audio, and subtitles
    final_video = CompositeVideoClip([video] + subtitle_clips)
    final_video = final_video.set_audio(audio)
    
    # Write output video
    final_video.write_videofile(output_path, codec="libx264", audio_codec="aac")
    
    return output_path