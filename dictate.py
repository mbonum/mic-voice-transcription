import os
import subprocess
import tempfile
from datetime import datetime

from faster_whisper import WhisperModel

MODEL = "large-v3"

OUTPUT_DIR = os.path.expanduser("~/Dev/dji-mic-voice-transcription/recordings")

os.makedirs(OUTPUT_DIR, exist_ok=True)


print("Loading Whisper...")
model = WhisperModel(
    MODEL,
    device="cuda",
    compute_type="float16",
)

print("Ready.")
print()
print("Press ENTER to start recording...")
input()

with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
    audio_file = f.name

print("🎙️ Recording... Press ENTER to stop.")

process = subprocess.Popen(
    [
        "pw-record",
        "--target",
        "alsa_input.usb-DJI_Technology_Co.__Ltd._DJI_MIC_MINI_XSP12345678B-01.analog-stereo",
        audio_file,
    ]
)

input()

process.terminate()
process.wait()

print("🧠 Transcribing...")

segments, info = model.transcribe(
    audio_file,
    language="en",
    beam_size=5,
)

text = " ".join(segment.text.strip() for segment in segments).strip()

now = datetime.now()

filename = now.strftime("%Y-%m-%d_%H-%M-%S.md")

output_file = os.path.join(OUTPUT_DIR, filename)

markdown = f"""# Voice transcription

**Date:** {now.strftime("%Y-%m-%d %H:%M:%S")}

{text}
"""

with open(output_file, "w", encoding="utf-8") as f:
    f.write(markdown)

os.unlink(audio_file)

print()
print("✅ Transcription saved:")
print(output_file)
print()
print(text)
