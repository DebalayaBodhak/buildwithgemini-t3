import os
import glob
import subprocess

def get_video_duration(video_path):
    cmd = [
        "ffprobe", "-v", "error", "-show_entries",
        "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", video_path
    ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return float(result.stdout.strip())

def combine_video_audio(audio_file="lofi_background_music.wav", output_file="scenery_agent_demo.mp4"):
    video_files = glob.glob("video_raw/*.webm")
    if not video_files:
        raise FileNotFoundError("No raw video webm file found in video_raw/")
    raw_video = video_files[0]
    
    print(f"Raw video file found: {raw_video}")
    duration = get_video_duration(raw_video)
    print(f"Raw video duration: {duration:.2f} seconds")
    
    fade_out_start = max(0.0, duration - 2.0)
    
    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-i", raw_video,
        "-i", audio_file,
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-filter_complex", f"[1:a]afade=t=in:st=0:d=1.0,afade=t=out:st={fade_out_start:.2f}:d=2.0[a]",
        "-map", "0:v:0",
        "-map", "[a]",
        "-shortest",
        output_file
    ]
    
    print(f"Running ffmpeg command to blend video & upbeat lo-fi audio...")
    res = subprocess.run(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
        print("FFmpeg error output:")
        print(res.stderr)
        raise RuntimeError("FFmpeg processing failed!")
        
    print(f"Final video successfully generated: {output_file}")
    
    # Also copy to assets and artifacts directory for easy access & user preview!
    assets_dir = "/config/Desktop/t3/assets"
    os.makedirs(assets_dir, exist_ok=True)
    asset_target = os.path.join(assets_dir, "scenery_agent_demo.mp4")
    subprocess.run(["cp", output_file, asset_target])
    print(f"Copied demo video to assets: {asset_target}")

    artifact_dir = "/config/.gemini/antigravity/brain/63a161d9-c9da-4c72-abe5-b3af0239fce9"
    os.makedirs(artifact_dir, exist_ok=True)
    artifact_target = os.path.join(artifact_dir, "scenery_agent_demo.mp4")
    subprocess.run(["cp", output_file, artifact_target])
    print(f"Copied demo video to artifacts directory: {artifact_target}")

if __name__ == "__main__":
    combine_video_audio()
