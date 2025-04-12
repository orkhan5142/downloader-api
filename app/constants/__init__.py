# app/constants/__init__.py

# Define the available audio qualities (bitrates)
AUDIO_QUALITIES = [
    {"abr": "128kbps", "mime_type": "audio/mp4"},
    {"abr": "192kbps", "mime_type": "audio/webm"},
    {"abr": "256kbps", "mime_type": "audio/mp4"},
    {"abr": "320kbps", "mime_type": "audio/mp4"}
]

# Define the available video resolutions
VIDEO_RESOLUTIONS = [
    "144p", "240p", "360p", "480p", "720p", "1080p", "1440p", "2160p"
]