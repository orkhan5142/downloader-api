#!/bin/bash


pip install -r requirements.txt


python -c "import whisper; print('Downloading Whisper model...'); whisper.load_model('base'); print('Model downloaded.')"