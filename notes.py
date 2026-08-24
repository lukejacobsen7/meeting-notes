#!/usr/bin/env python3
"""
meeting-notes — offline "who said what" transcript. No account, no API key, no upload.

    notes.py <audio-or-video> [--speakers N] [--model NAME] [--name 1=Luke --name 2=Michael]

Diarization: sherpa-onnx (pyannote segmentation + NeMo TitaNet embeddings), ungated models.
Transcription: mlx-whisper on the Apple Silicon GPU.
Everything runs locally. Validated 2026-08-20 on a real 4-speaker reference clip: 4/4 speakers,
32x realtime.

NOTE: macOS `say` voices are NOT a valid test fixture -- the embedding model cannot separate
them (they share a TTS engine). Test with real human speech or you will chase a phantom bug.
"""
import argparse, os, subprocess, sys, tempfile, json

HERE = os.path.dirname(os.path.abspath(__file__))
MODELS = os.path.join(HERE, "models")
SEG = os.path.join(MODELS, "sherpa-onnx-pyannote-segmentation-3-0", "model.onnx")
EMB = os.path.join(MODELS, "nemo_en_titanet_large.onnx")


def to_wav(src):
    """Anything ffmpeg reads -> 16k mono wav."""
    out = os.path.join(tempfile.mkdtemp(prefix="mn_"), "audio.wav")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", src,
                    "-ar", "16000", "-ac", "1", out], check=True)
    return out


def diarize(wav, n_speakers):
    import sherpa_onnx, soundfile as sf
    clustering = (sherpa_onnx.FastClusteringConfig(num_clusters=n_speakers)
                  if n_speakers > 0 else
                  sherpa_onnx.FastClusteringConfig(num_clusters=-1, threshold=0.5))
    cfg = sherpa_onnx.OfflineSpeakerDiarizationConfig(
        segmentation=sherpa_onnx.OfflineSpeakerSegmentationModelConfig(
            pyannote=sherpa_onnx.OfflineSpeakerSegmentationPyannoteModelConfig(model=SEG),
            num_threads=4),
        embedding=sherpa_onnx.SpeakerEmbeddingExtractorConfig(model=EMB, num_threads=4),
        clustering=clustering, min_duration_on=0.3, min_duration_off=0.5)
    if not cfg.validate():
        sys.exit("diarization config invalid -- are the models in ./models ?")
    audio, _ = sf.read(wav, dtype="float32")
    sd = sherpa_onnx.OfflineSpeakerDiarization(cfg)
    return [(s.start, s.end, s.speaker) for s in sd.process(audio).sort_by_start_time()]


def transcribe(wav, model):
    import mlx_whisper
    r = mlx_whisper.transcribe(wav, path_or_hf_repo=model, word_timestamps=True,
                               condition_on_previous_text=False)
    words = []
    for seg in r.get("segments", []):
        for w in seg.get("words", []) or []:
            words.append((w["start"], w["end"], w["word"]))
    if not words:  # fall back to segment granularity
        words = [(s["start"], s["end"], s["text"]) for s in r.get("segments", [])]
    return words


def speaker_at(t, turns):
    """Speaker whose turn contains t; else the nearest turn (whisper and the diarizer
    disagree by a few hundred ms at boundaries, and an unlabelled word is worse than a
    slightly-misplaced one)."""
    for a, b, spk in turns:
        if a <= t <= b:
            return spk
    if not turns:
        return 0
    return min(turns, key=lambda x: min(abs(t - x[0]), abs(t - x[1])))[2]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("audio")
    ap.add_argument("--speakers", type=int, default=0, help="exact count if you know it (recommended)")
    ap.add_argument("--model", default="mlx-community/whisper-large-v3-turbo")
    ap.add_argument("--name", action="append", default=[], metavar="N=Name",
                    help="label a speaker, e.g. --name 0=Luke")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    names = {}
    for n in a.name:
        k, _, v = n.partition("=")
        names[int(k)] = v

    print("[1/3] converting audio ...", flush=True)
    wav = to_wav(a.audio)
    print("[2/3] finding speakers ...", flush=True)
    turns = diarize(wav, a.speakers)
    found = sorted({t[2] for t in turns})
    print(f"      {len(found)} speaker(s), {len(turns)} turns", flush=True)
    print("[3/3] transcribing (first run downloads the model) ...", flush=True)
    words = transcribe(wav, a.model)

    # stitch words into contiguous same-speaker blocks
    lines, cur, cur_spk, cur_start = [], [], None, 0.0
    for st, en, w in words:
        spk = speaker_at((st + en) / 2, turns)
        if spk != cur_spk and cur:
            lines.append((cur_start, cur_spk, "".join(cur).strip()))
            cur, cur_start = [], st
        if not cur:
            cur_start = st
        cur_spk = spk
        cur.append(w if w.startswith(" ") else " " + w)
    if cur:
        lines.append((cur_start, cur_spk, "".join(cur).strip()))

    def stamp(t):
        return f"{int(t)//60:02d}:{int(t)%60:02d}"

    out = []
    for t, spk, text in lines:
        if not text:
            continue
        who = names.get(spk, f"Speaker {spk + 1}")
        out.append(f"[{stamp(t)}] {who}: {text}")
    body = "\n\n".join(out)

    dest = a.out or (os.path.splitext(a.audio)[0] + "-transcript.txt")
    with open(dest, "w") as f:
        f.write(body + "\n")
    print("\n" + body[:1500] + ("\n..." if len(body) > 1500 else ""))
    print(f"\nsaved -> {dest}")


if __name__ == "__main__":
    main()
