#!/usr/bin/env python3
"""Word-level speech beats for /cine-grade (shared format with /cine-multicam).

Transcribes a local video with Whisper (word timestamps), then prints:
  DURATION, LANGUAGE, WORDS (start/end/word), GAPS (silences >= 0.25s),
  NAIVE_CUTS (deterministic cut-point suggestions; shots = cuts + 1).

The script reports facts; semantic refinement (phrase meaning, visual events,
shot design) is Claude's job.
Idempotent: reuses <video stem>.json if present unless --force.
"""
import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

MIN_GAP = 0.25       # silence >= this between words counts as a breath/pause
MIN_SPACING = 1.5    # minimum seconds between suggested cuts (cine shots run >= ~2s)
FIRST_CUT_LO = 2.5   # the opening shot breathes: it holds at least this long
FIRST_CUT_HI = 5.5   # ...and cut 1 should land by about here
FIRST_CUT_AIM = 4.0  # preferred landing zone for cut 1
TAIL_GUARD = 2.0     # last cut must be <= duration - this (closing shot breathes too)

# don't end the opening shot right after a function word (mid-phrase cut)
FUNCTION_WORDS = {
    "the", "a", "an", "to", "of", "in", "on", "at", "and", "or", "but", "if",
    "is", "are", "was", "i", "you", "it", "my", "your", "this", "that", "for",
    "o", "os", "as", "um", "uma", "de", "do", "da", "dos", "das", "que", "e",
    "em", "no", "na", "nos", "nas", "pra", "para", "com", "se", "eu", "meu",
    "minha", "seu", "sua", "por", "mais",
}


def is_function_word(word: str) -> bool:
    return word.lower().strip(".,!?;:…") in FUNCTION_WORDS


def die(msg: str, code: int = 2):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def ffprobe_duration(video: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(video)],
        capture_output=True, text=True)
    if out.returncode != 0:
        die(f"ffprobe failed on {video}:\n{out.stderr.strip()}")
    return float(out.stdout.strip())


def transcribe(video: Path, model: str, language: str | None):
    # single --output_format: whisper's argparse keeps only the last one given,
    # and the word table is read from the JSON (no SRT needed here)
    cmd = ["whisper", str(video), "--model", model, "--word_timestamps", "True",
           "--output_format", "json",
           "--output_dir", str(video.parent)]
    if language:
        cmd += ["--language", language]
    print(f"# transcribing with whisper --model {model} (first run may download the model)...",
          file=sys.stderr)
    out = subprocess.run(cmd, capture_output=True, text=True)
    if out.returncode != 0:
        die(f"whisper failed:\n{out.stderr.strip()[-2000:]}")


def load_words(json_path: Path):
    with open(json_path, "r", encoding="utf-8") as f:
        d = json.load(f)
    words = []
    for seg in d.get("segments", []):
        for w in seg.get("words", []):
            words.append({"word": w["word"].strip(),
                          "start": float(w["start"]), "end": float(w["end"])})
    return d.get("language", "unknown"), words


def naive_cuts(words, duration: float, n: int = 6):
    """Deterministic first guess: cut 1 ends the opening shot (~2.5-5.5s),
    remaining cuts land in the largest silences, gaps filled at word starts."""
    lo, hi = FIRST_CUT_LO, duration - TAIL_GUARD
    if hi <= lo:  # video too short to place cuts sanely
        return [], True

    # cut 1: word end closest to FIRST_CUT_AIM within [FIRST_CUT_LO, FIRST_CUT_HI],
    # skipping function words (a cut right after "the"/"to" lands mid-phrase)
    c1 = None
    in_range = [w for w in words if FIRST_CUT_LO <= w["end"] <= FIRST_CUT_HI]
    candidates = [w["end"] for w in in_range if not is_function_word(w["word"])]
    if not candidates:
        candidates = [w["end"] for w in in_range]
    if candidates:
        c1 = min(candidates, key=lambda t: abs(t - FIRST_CUT_AIM))
    else:
        after = [w["end"] for w in words if w["end"] > FIRST_CUT_LO]
        c1 = after[0] if after else min(FIRST_CUT_AIM, hi)
    chosen = [round(min(c1, hi), 1)]

    # gaps sorted by size desc; cut lands at the gap start (end of previous word)
    gaps = []
    for a, b in zip(words, words[1:]):
        g = b["start"] - a["end"]
        if g >= MIN_GAP:
            gaps.append({"at": a["end"], "size": g, "after": a["word"]})
    for g in sorted(gaps, key=lambda x: -x["size"]):
        if len(chosen) >= n:
            break
        t = round(g["at"], 1)
        if lo <= t <= hi and all(abs(t - c) >= MIN_SPACING for c in chosen):
            chosen.append(t)

    # fill remainder: midpoint of the largest open interval, snapped to a word start
    starts = sorted(w["start"] for w in words)
    while len(chosen) < n:
        pts = sorted(chosen)
        intervals = list(zip([lo] + pts, pts + [hi]))
        a, b = max(intervals, key=lambda iv: iv[1] - iv[0])
        if b - a < 2 * MIN_SPACING:
            break  # no room left; report fewer than 4
        mid = (a + b) / 2
        snapped = min(starts, key=lambda s: abs(s - mid)) if starts else mid
        t = round(min(max(snapped, a + MIN_SPACING), b - MIN_SPACING), 1)
        if all(abs(t - c) >= MIN_SPACING for c in chosen):
            chosen.append(t)
        else:
            chosen.append(round(mid, 1))
    return sorted(set(chosen)), False


def main():
    ap = argparse.ArgumentParser(description="Word-level beats for /cine-multicam")
    ap.add_argument("video", type=Path)
    ap.add_argument("--model", default="small", help="whisper model (default: small)")
    ap.add_argument("--cuts", type=int, default=6,
                    help="number of cut points to suggest (shots = cuts + 1; default: 6)")
    ap.add_argument("--language", default=None, help="force language code, e.g. pt, en")
    ap.add_argument("--force", action="store_true", help="retranscribe even if .json exists")
    args = ap.parse_args()

    try:  # Windows consoles may be cp1252; transcripts may not be
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    missing = [t for t in ("ffprobe", "whisper") if not shutil.which(t)]
    if missing:
        die(f"missing required tools: {', '.join(missing)} "
            f"(run scripts/check_env.py for the install commands)")
    if not args.video.exists():
        die(f"video not found: {args.video}")

    duration = ffprobe_duration(args.video)
    json_path = args.video.with_suffix(".json")
    if args.force or not json_path.exists():
        transcribe(args.video, args.model, args.language)
    if not json_path.exists():
        die(f"whisper produced no JSON at {json_path}")

    language, words = load_words(json_path)

    print(f"DURATION: {duration:.2f}")
    print(f"LANGUAGE: {language}")

    if not words:
        print("NO_SPEECH: true")
        step = duration / (args.cuts + 1)
        even = [round(step * i, 1) for i in range(1, args.cuts + 1) if step * i <= duration - TAIL_GUARD]
        print("NAIVE_CUTS (evenly spaced fallback, no speech to anchor on):")
        for t in even:
            print(f"  {t}")
        return

    print("\nWORDS:")
    for w in words:
        print(f"  {w['start']:6.2f} -> {w['end']:6.2f}  {w['word']}")

    print("\nGAPS (silences >= %.2fs):" % MIN_GAP)
    any_gap = False
    for a, b in zip(words, words[1:]):
        g = b["start"] - a["end"]
        if g >= MIN_GAP:
            any_gap = True
            print(f"  after '{a['word']}': {a['end']:.2f} -> {b['start']:.2f}  (gap {g:.2f}s)")
    if not any_gap:
        print("  (none)")

    cuts, too_short = naive_cuts(words, duration, args.cuts)
    if too_short:
        print(f"\nSHORT_VIDEO: true (no sane room for {args.cuts} cuts)")
    print("\nNAIVE_CUTS (deterministic first guess -- refine against phrase meaning):")
    for t in cuts:
        print(f"  {t}")
    if duration > 30:
        print(f"LONG_VIDEO: true (>30s; the technique shines on 15-30s takes -- "
              f"consider the strongest window, and mind the generation-length cap)")


if __name__ == "__main__":
    main()
