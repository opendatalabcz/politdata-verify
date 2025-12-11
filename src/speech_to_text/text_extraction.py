import time
from tkinter import EventType

from deepgram import DeepgramClient
from faster_whisper import WhisperModel
import os
from dotenv import load_dotenv
load_dotenv()

DG_API_KEY = os.getenv("DG_API_KEY")
audio_path = "../../data/test_audio.mp3"

# ----- Step 1: Transcribe locally -----
start_time = time.perf_counter()
whisper = WhisperModel("large-v3", device="cpu")
segments, info = whisper.transcribe("../../data/test_audio.mp3", word_timestamps=True, language="cs")

# Combine into one text chunk
for segment in segments:
    print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))
end_time = time.perf_counter()
print(f"Transcription took {end_time - start_time:.2f} seconds")
