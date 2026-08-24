# meeting-notes — free, offline, who-said-what transcripts

Nothing is uploaded. No account, no API key, no gated models.

## Capturing a ZOOM call — best option first

**1. Zoom's own local recording (easiest, and it gives PERFECT speaker labels)**

You have to announce the recording anyway — Florida is an all-party consent state — so ask the
host for recording permission in the same breath. If you get it:

- Zoom → **Record** → *Record on this Computer* (free tier supports local recording)
- Settings → Recording → tick **"Record a separate audio file for each participant"**
  ← this is the magic one: you get one audio file per person, so you already know who said what
  and **no diarization is needed at all**
- Files land in `~/Documents/Zoom/<meeting>/`

Then just transcribe each file:
```
./run.sh ~/Documents/Zoom/<meeting>/audio_only_Dana.m4a 1 --name 0=Dana
```

**2. If you can't record in Zoom — capture the system audio yourself**

macOS won't let an app record other apps' audio without a virtual device. Install the free
MIT-licensed one (needs your admin password):

```
brew install --cask blackhole-2ch
```

Then **Audio MIDI Setup** (in /Applications/Utilities):
- **+ → Create Multi-Output Device** → tick your headphones/speakers **and** BlackHole 2ch.
  Set this as your Mac's **output** so you still hear the call while it's being captured.
- **+ → Create Aggregate Device** → tick **BlackHole 2ch** and your **microphone**.
  Name it anything with "Aggregate" in it. This is what gets recorded.

Then:
```
./record.sh                 # auto-detects the aggregate device
```

**3. Last resort, zero setup:** put Zoom on the laptop **speakers** (not headphones) and run
`./record.sh` — the built-in mic picks up the room. Works, sounds worse, diarization still fine.

## Turning audio into a transcript

```
./run.sh <file> <n_speakers> [--name 0=Alex --name 1=Dana ...]
```

Accepts any audio **or video** file ffmpeg can read. Passing the exact speaker count is much more
reliable than letting it guess. Output is saved next to the input as `<name>-transcript.txt`:

```
[00:00] Alex: Before we start, I want to walk through where the build actually stands.
[00:16] Dana: That's the part I care about.
```

## Known-good / known-bad

- ✅ Validated on a real 4-speaker clip: **4/4 speakers, correct turns, ~10x realtime**, and it
  correctly re-identified a speaker returning later in the call.
- 🔴 **macOS `say` voices are NOT a valid test fixture.** They share a TTS engine and the
  embedding model cannot separate them — a male and a female voice cluster together. Segmentation
  is fine; only clustering fails. Test with real speech.
- 🔴 First run downloads the whisper model (~1.5GB). **Do that before the meeting, not during.**

## Legal

**Fla. Stat. § 934.03 — all-party consent. Recording without everyone's consent is a
third-degree felony**, and it covers a transcript, not just audio. Say it before anything
substantive and get an audible yes from each person:

> "Quick note before we get going — I'm recording this so I can take accurate notes.
>  Everyone okay with that?"
