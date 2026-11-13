import argparse
import os
import subprocess
import tempfile
from datetime import datetime

from faster_whisper import WhisperModel

MODEL = "large-v3"

DEFAULT_DEVICE = (
    "alsa_input.usb-DJI_Technology_Co.__Ltd._DJI_MIC_MINI_XSP12345678B-01.analog-stereo"
)
DEFAULT_OUTPUT_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "recordings"
)

parser = argparse.ArgumentParser(
    description="Record from a mic and transcribe locally with Whisper."
)
parser.add_argument(
    "--device",
    default=DEFAULT_DEVICE,
    help="PipeWire source to record from (list sources with `pw-record -l`)",
)
parser.add_argument(
    "--output-dir",
    default=DEFAULT_OUTPUT_DIR,
    help="Directory to save .md transcripts (default: ./recordings next to this script)",
)
parser.add_argument(
    "--language",
    default="en",
    help="Spoken language code for Whisper (default: en)",
)
args = parser.parse_args()

OUTPUT_DIR = args.output_dir
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
        args.device,
        audio_file,
    ]
)

input()

process.terminate()
process.wait()

if os.path.getsize(audio_file) <= 44:  # only a bare WAV header
    print("⚠️ Nothing recorded (empty file), skipping transcription.")
    os.unlink(audio_file)
    raise SystemExit(0)

print("🧠 Transcribing...")

segments, info = model.transcribe(
    audio_file,
    language=args.language,
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
