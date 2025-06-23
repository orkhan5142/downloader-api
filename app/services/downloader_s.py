import yt_dlp
import os
from typing import Optional, Dict, Any, Tuple

class DownloadService:
    @staticmethod
    def detect_platform(url: str) -> str:
        """Detect which platform the URL is from"""
        if "youtube.com" in url or "youtu.be" in url:
            return "YouTube"
        elif "instagram.com" in url:
            return "Instagram"
        elif "tiktok.com" in url:
            return "TikTok"
        elif "facebook.com" in url or "fb.com" in url or "fb.watch" in url:
            return "Facebook"
        else:
            return "Unknown"

    @staticmethod
    def get_available_formats(url: str) -> Tuple[bool, Dict[str, Any]]:
        """Get available formats for the given URL"""
        ydl_opts = {
            'quiet': True,
            'skip_download': True
        }
        
        formats_info = {"formats": [], "message": ""}
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if info and 'formats' in info:
                    # 1. Ən yaxşı audio formatının ölçüsünü tapırıq
                    best_audio_size = 0
                    for format_item in info['formats']:
                        if format_item.get('acodec') != 'none' and format_item.get('vcodec') == 'none':  # Sadəcə audio formatları
                            current_size = format_item.get('filesize', 0) or 0
                            if current_size > best_audio_size:
                                best_audio_size = current_size

                    # 2. Formatları işləyib, copy_format_info-da cəmləyirik
                    for format_item in info['formats']:
                        original_size = format_item.get('filesize', 0) or 0
                        total_size = original_size + best_audio_size  # Əsas format + best audio ölçüsü

                        format_info = {
                            "format_id": format_item.get('format_id', 'N/A'),
                            "ext": format_item.get('ext', 'N/A'),
                            "resolution": format_item.get('resolution', 'N/A'),
                            "filesize": original_size,
                            "format_note": format_item.get('format_note', 'N/A'),
                            "vcodec": format_item.get('vcodec', 'none'),
                            "acodec": format_item.get('acodec', 'none'),
                            "fps": format_item.get('fps', None),
                            "tbr": format_item.get('tbr', None),
                            "protocol": format_item.get('protocol', None)
                        }
                        copy_format_info = {
                            "format_id": format_item.get('format_id', 'N/A'),
                            "ext": format_item.get('ext', 'N/A'),
                            "resolution": format_item.get('resolution', 'N/A'),
                            "filesize": total_size,  # Əsas format + best audio cəmi
                            "format_note": format_item.get('format_note', 'N/A'),
                            "vcodec": format_item.get('vcodec', 'none'),
                            "acodec": 'example',  # Audio codec-i əvəz edirik
                            "fps": format_item.get('fps', None),
                            "tbr": format_item.get('tbr', None),
                            "protocol": format_item.get('protocol', None)
                        }
                        formats_info["formats"].append(format_info)
                        formats_info["formats"].append(copy_format_info)
                    
                    formats_info["title"] = info.get('title', 'Unknown title')
                    formats_info["duration"] = info.get('duration', 0)
                    formats_info["thumbnail"] = info.get('thumbnail', '')
                    return True, formats_info
                else:
                    formats_info["message"] = "No format information available"
                    return False, formats_info
        except Exception as e:
            formats_info["message"] = f"Error fetching formats: {str(e)}"
            return False, formats_info
    @staticmethod
    def prepare_download(url: str, download_type: str, format_id: Optional[str] = None) -> Dict[str, Any]:
        """Prepare download and return filename without downloading"""
        try:
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(url, download=False)
                if not info:
                    raise Exception("Could not get video info")
                
                if download_type == "video":
                    ext = 'mp4'
                elif download_type == "video only":
                    ext = 'mp4'
                elif download_type == "audio":
                    ext = 'm4a'
                
                filename = f"{info['title']}.{ext}"
                
                return {
                    "success": True,
                    "filename": filename,
                    "message": "Ready for streaming download"
                }
        except Exception as e:
            return {
                "success": False,
                "message": str(e)
            }

    @staticmethod
    def download_media(url: str, download_type: str, format_id: Optional[str] = None) -> Dict[str, Any]:
        """Download media from any supported platform"""
        temp_dir = "/tmp/media_downloads"
        os.makedirs(temp_dir, exist_ok=True)
        
        result = {"success": False, "message": "", "filepath": ""}
        
        try:
            ydl_opts = {
                'outtmpl': f"{temp_dir}/%(title)s.%(ext)s",
                'quiet': True,
                'ignoreerrors': True,
                'nooverwrites': True,
                'ratelimit': 10000000,
            }

            # Platform-agnostic format selection
            if download_type == "video":
                if format_id:
                    # Try with requested format first
                    ydl_opts['format'] = f'{format_id}+bestaudio/best'
                else:
                    # Default to best quality
                    ydl_opts['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
                ydl_opts['merge_output_format'] = 'mp4'
                
            elif download_type == "video only":
                ydl_opts['format'] = format_id if format_id else 'bestvideo[ext=mp4]'
                
            elif download_type == "audio":
                ydl_opts['format'] = format_id if format_id else 'bestaudio/best'
                ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'm4a',
                    'preferredquality': '192',
                }]

            # Execute download with retry logic
            max_retries = 2
            for attempt in range(max_retries):
                try:
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(url, download=True)
                        if info:
                            file_ext = 'mp4' if download_type in ["video", "video only"] else 'm4a'
                            actual_filename = ydl.prepare_filename(info)
                            if download_type == "audio":
                                actual_filename = os.path.splitext(actual_filename)[0] + '.m4a'
                            
                            if os.path.exists(actual_filename):
                                result.update({
                                    "success": True,
                                    "message": "Download complete",
                                    "filepath": actual_filename,
                                    "filename": os.path.basename(actual_filename),
                                    "filesize": os.path.getsize(actual_filename)
                                })
                                return result
                            else:
                                result["message"] = "File was not created properly"
                except Exception as e:
                    if attempt == max_retries - 1:  # Last attempt
                        result["message"] = f"Error during download: {str(e)}"
                    else:
                        # On failure, try with more permissive format selection
                        if download_type == "video":
                            ydl_opts['format'] = 'bestvideo+bestaudio/best'
                        elif download_type == "video only":
                            ydl_opts['format'] = 'bestvideo'
                        elif download_type == "audio":
                            ydl_opts['format'] = 'bestaudio'
                        continue

            # Clean up if download failed
            if 'actual_filename' in locals() and os.path.exists(actual_filename):
                try:
                    os.remove(actual_filename)
                except:
                    pass
            
        except Exception as e:
            result["message"] = f"Unexpected error: {str(e)}"
        
        return result