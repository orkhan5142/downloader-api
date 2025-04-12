import os
import uuid
import subprocess
import requests
from pytubefix import YouTube
from fastapi.responses import StreamingResponse, FileResponse
from starlette.background import BackgroundTask
from app.constants import VIDEO_RESOLUTIONS, AUDIO_QUALITIES

def ensure_temp_directory():
    temp_dir = "temp_downloads"
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    return temp_dir

async def check_video_url(url):
    try:
        YouTube(url)
        return True
    except:
        return False

async def get_all_video_info(uri: str):
    if await check_video_url(uri):
        yt = YouTube(uri)

        # Fetch all available video resolutions dynamically
        available_resolutions = sorted(
            list(set([int(stream.resolution.split('p')[0]) for stream in yt.streams.filter(only_video=True) if 'p' in stream.resolution])),
            reverse=True
        )

        # Fetch all available audio bitrates dynamically, removing duplicates
        unique_audio = {}
        for stream in yt.streams.filter(only_audio=True):
            unique_audio[(stream.abr, stream.mime_type)] = {"abr": stream.abr, "mime_type": stream.mime_type}
        
        # Get the list of unique audio qualities
        available_audio = list(unique_audio.values())

        return {
            "title": yt.title,
            "resolutions": available_resolutions,
            "audio": available_audio
        }
    else:
        return {"error": "Invalid YouTube URL"}

async def download_audio(abr: str, uri: str):
    if await check_video_url(uri):
        yt = YouTube(uri)
        audio_stream = yt.streams.filter(only_audio=True, abr=abr).first()
        if audio_stream:
            audio_url = audio_stream.url
            response = requests.get(audio_url, stream=True)
            return StreamingResponse(
                response.iter_content(chunk_size=1024),
                media_type="audio/mpeg",
                headers={"Content-Disposition": f"attachment; filename={yt.title}.mp3"}
            )
        else:
            return {"error": "Audio stream not found"}
    else:
        return {"error": "Invalid URL"}

async def download_video(res: str, uri: str):
    if await check_video_url(uri):
        yt = YouTube(uri)
        # Try to get a progressive stream (video + audio) first
        stream = yt.streams.filter(res=res, progressive=True).first()
        if stream:
            video_url = stream.url
            response = requests.get(video_url, stream=True)
            return StreamingResponse(
                response.iter_content(chunk_size=1024),
                media_type="video/mp4",
                headers={"Content-Disposition": f"attachment; filename={yt.title}.mp4"}
            )
        else:
            # If no progressive stream, download video and audio separately
            video_stream = yt.streams.filter(res=res, only_video=True).first()
            if video_stream:
                # Download video
                video_url = video_stream.url
                video_response = requests.get(video_url, stream=True)

                # Download selected audio stream
                audio_abr = '128kbps'  # Default audio bitrate (can be changed based on user choice)
                audio_stream = yt.streams.filter(only_audio=True, abr=audio_abr).first()
                audio_url = audio_stream.url
                audio_response = requests.get(audio_url, stream=True)

                # Create a temporary file to save merged video and audio
                temp_dir = ensure_temp_directory()
                video_path = os.path.join(temp_dir, f"{uuid.uuid4()}.mp4")
                audio_path = os.path.join(temp_dir, f"{uuid.uuid4()}.mp3")
                merged_path = os.path.join(temp_dir, f"{uuid.uuid4()}.mp4")

                # Save video and audio to temporary files
                with open(video_path, 'wb') as video_file:
                    for chunk in video_response.iter_content(chunk_size=1024):
                        video_file.write(chunk)

                with open(audio_path, 'wb') as audio_file:
                    for chunk in audio_response.iter_content(chunk_size=1024):
                        audio_file.write(chunk)

                # Merge video and audio using ffmpeg
                try:
                    ffmpeg_command = [
                        'ffmpeg',
                        '-i', video_path,
                        '-i', audio_path,
                        '-c:v', 'copy',  # Copy video stream without re-encoding
                        '-c:a', 'aac',   # Use AAC for audio encoding
                        '-strict', 'experimental',  # Allow experimental features (if needed)
                        merged_path
                    ]
                    subprocess.run(ffmpeg_command, check=True)

                    # Return the merged file
                    response = FileResponse(
                        path=merged_path,
                        media_type="video/mp4",
                        filename=f"{yt.title}.mp4"
                    )

                    # Add background task to delete the file after response is sent
                    response.background = BackgroundTask(lambda: os.remove(merged_path))
                    return response
                except Exception as e:
                    return {"error": f"An error occurred while merging: {str(e)}"}
                finally:
                    # Cleanup temporary files
                    os.remove(video_path)
                    os.remove(audio_path)
            else:
                return {"error": "Video stream not found"}
    else:
        return {"error": "Invalid URL"}
