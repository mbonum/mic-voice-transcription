# DJI Mic Voice Transcription

Dictate into a **DJI Mic Mini** over USB and get a timestamped Markdown transcript, transcribed **100% locally** with [faster-whisper](https://github.com/SYSTRAN/faster-whisper) (`large-v3`) on an NVIDIA GPU. No cloud, no API keys.

## How it works

`dictate.py` does three things in sequence:

1. **Records** — streams audio from the mic via `pw-record` (PipeWire) into a temporary `.wav`.
2. **Transcribes** — runs the transcript through Whisper `large-v3` (CUDA, float16, beam search, English).
3. **Saves** — writes `recordings/YYYY-MM-DD_HH-MM-SS.md` with a date header and the text, prints the transcript, and deletes the temp audio file.

## Requirements

- The DJI Mic Mini plugged in over USB (it shows up as an ALSA/PipeWire device).
- [PipeWire](https://pipewire.org/) with the `pw-record` CLI available.
- Python 3 with the pinned deps: `pip install -r requirements.txt`
- An **NVIDIA GPU** — the model is hardcoded to `device="cuda"` / `float16`. On a CPU-only machine you must edit `WhisperModel(...)` (e.g. `device="cpu", compute_type="int8"`); expect it to be slow.

## Usage

```sh
source .venv/bin/activate   # or however you set up the env
python dictate.py
```

Options (`python dictate.py --help` for details):

- `--device` — PipeWire source to record from (default: the DJI Mic Mini; list sources with `pw-record -l`)
- `--output-dir` — where to save the `.md` files (default: `recordings/` next to the script)
- `--language` — spoken language code for Whisper (default: `en`)

1. Wait for `Ready.` (first run downloads the ~3 GB `large-v3` model to `~/.cache/huggingface`).
2. Press **ENTER** to start recording.
3. Talk. Press **ENTER** to stop.
4. The transcript is saved under `recordings/` (gitignored) and printed to the terminal.

## Notes & gotchas

- **Different mic or unit?** The default `--device` targets a DJI Mic Mini; PipeWire names include the mic's USB serial, so a different unit gets a different name. Find yours with `pw-record -l` (or `pactl list sources`) and pass it via `--device`.
- **Whisper repetition artifacts**: on long, unbroken monologues Whisper can repeat a phrase several times in a row. If it bothers you, try shorter recordings, or add `condition_on_previous_text=False` to `model.transcribe(...)` to reduce the loop.
- **Empty recording**: if you stop immediately, the script detects the header-only WAV and exits cleanly instead of wasting time on a transcription.
