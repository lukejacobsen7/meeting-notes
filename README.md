<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/logo-dark.svg">
    <img alt="meeting-notes" src="assets/logo-light.svg" width="540">
  </picture>
</p>

<p align="center">
  <img alt="python" src="https://img.shields.io/badge/python-3.10%2B-2BD9FF">
  <img alt="runs" src="https://img.shields.io/badge/runs-100%25%20offline-2BD9FF">
  <img alt="cost" src="https://img.shields.io/badge/cost-$0-2BD9FF">
  <a href="LICENSE"><img alt="license" src="https://img.shields.io/badge/license-MIT-2BD9FF"></a>
</p>

<p align="center">
  <a href="#quick-start">Quick Start</a> ·
  <a href="#capturing-a-zoom-call">Capture a call</a> ·
  <a href="#turning-audio-into-a-transcript">Transcribe</a> ·
  <a href="#known-good--known-bad">Known good / bad</a> ·
  <a href="#legal">Legal</a>
</p>

**Who said what, in a meeting, for free — on your own machine.**

Point it at any audio or video file and get back a timestamped transcript with each speaker
labelled by name. Nothing is uploaded. No account, no API key, no gated models, no per-minute
billing. It runs Whisper for the words and a speaker-embedding model for the turns, both locally.

```
[00:00] Alex: Before we start, I want to walk through where the build actually stands.
[00:16] Dana: That's the part I care about.
[00:31] Alex: Fair. The short version is the API is done and the UI is not.
```

## Quick start

```bash
./run.sh <file> <n_speakers> [--name 0=Alex --name 1=Dana ...]
```

| Argument | Meaning |
| --- | --- |
| `<file>` | Any audio **or** video file ffmpeg can read |
| `<n_speakers>` | Exact speaker count. Passing it is far more reliable than letting it guess |
| `--name N=Label` | Renames cluster `N`. Run once without it to see which is which |

Output lands next to the input as `<name>-transcript.txt`.

> **First run downloads the Whisper model (~1.5 GB).** Do that before the meeting, not during it.

## Capturing a Zoom call

Three options, best first.

### 1. Zoom's own local recording — easiest, and it gives perfect speaker labels

You have to announce the recording anyway (see [Legal](#legal)), so ask the host for permission in
the same breath. If you get it:

- Zoom → **Record** → *Record on this Computer*. The free tier supports local recording.
- Settings → Recording → tick **"Record a separate audio file for each participant."**
  This is the one that matters: you get one file per person, so you already know who said what and
  **no diarization is needed at all**.
- Files land in `~/Documents/Zoom/<meeting>/`.

```bash
./run.sh ~/Documents/Zoom/<meeting>/audio_only_Dana.m4a 1 --name 0=Dana
```

### 2. Capture the system audio yourself

macOS won't let an app record another app's audio without a virtual device. Install the free,
MIT-licensed one (needs your admin password):

```bash
brew install --cask blackhole-2ch
```

Then open **Audio MIDI Setup** (`/Applications/Utilities`):

| Device to create | Tick | Purpose |
| --- | --- | --- |
| **Multi-Output Device** | your headphones/speakers **and** BlackHole 2ch | Set as the Mac's *output* so you still hear the call while it is captured |
| **Aggregate Device** | BlackHole 2ch **and** your microphone | This is what gets recorded. Name it with "Aggregate" in it |

```bash
./record.sh      # auto-detects the aggregate device
```

### 3. Last resort, zero setup

Put the call on the laptop **speakers** (not headphones) and run `./record.sh` — the built-in mic
picks up the room. It works, it sounds worse, and diarization is still fine.

## Turning audio into a transcript

`run.sh` does the whole chain: ffmpeg decode → Whisper transcription → speaker embedding →
clustering → merge into labelled turns.

Passing the exact speaker count is the single biggest accuracy lever, because clustering an unknown
number of speakers is a much harder problem than splitting a known one.

## Known good / known bad

- ✅ Validated on a real 4-speaker clip: **4/4 speakers, correct turns, ~10× realtime**, and it
  correctly re-identified a speaker who returned later in the call.
- 🔴 **macOS `say` voices are not a valid test fixture.** They share one TTS engine, so the
  embedding model cannot separate them — a male and a female voice cluster together. Segmentation
  is fine; only clustering fails. Test with real speech.
- 🔴 First run downloads the Whisper model (~1.5 GB). Pre-warm it.

## Legal

**Fla. Stat. § 934.03 is all-party consent. Recording without everyone's consent is a
third-degree felony**, and it covers a transcript, not just the audio.

Say it before anything substantive and get an audible yes from each person:

> "Quick note before we get going — I'm recording this so I can take accurate notes.
> Everyone okay with that?"

Other states differ. Check yours.

## License

MIT — see [LICENSE](LICENSE).
