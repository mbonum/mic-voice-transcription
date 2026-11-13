import os
import subprocess
import tempfile

from faster_whisper import WhisperModel

MODEL = "large-v3"

model = WhisperModel(
    MODEL,
    device="cuda",
    compute_type="float16",
)

with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
    audio_file = f.name

print("Press ENTER to start recording...")
input()

print("🎙️ Recording... Press ENTER to stop.")

process = subprocess.Popen([
    "pw-record",
    "--target",
    "alsa_input.usb-DJI_Technology_Co.__Ltd._DJI_MIC_MINI_XSP12345678B-01.analog-stereo",
    audio_file,
])

input()

process.terminate()
process.wait()

print("🧠 Transcribing...")

segments, info = model.transcribe(
    audio_file,
    language="en",
    beam_size=5,
)

text = " ".join(segment.text.strip() for segment in segments)

print()
print("────────────────────────")
print(text)
print("────────────────────────")

os.unlink(audio_file)
