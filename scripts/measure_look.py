#!/usr/bin/env python3
"""Measure the look of a take (and of a target film frame): hue, saturation, black level, contrast.

The film's look is decomposed from memory or from one still, and the "delta check" (does the
target film change the take enough to read?) is a judgment call. This script gives numbers for
both, so the delta check and the result checks of a generation are objective.

Usage:
    python measure_look.py <take> [<target>] [--at SECONDS] [--target-at SECONDS]
                           [--frames N] [--role take|result] [--json]

  <take>     a video or an image: the raw take (default role) or the generated result (--role result)
  <target>   optional: a still or a clip of the target film's look
  --at       the second to sample in a video (default: 3 frames at 20, 50 and 80 percent)
  --role     take   the first file is the raw take: judge whether the target look will read (delta check)
             result the first file is the generated video: compare it with the target and name the
                    troubleshooting.md reinforcement for every axis that is off

Measured on a small copy of the frame(s): dominant and second hue, how colorful the frame is,
mean saturation, split tone (hue of the shadows against the highlights), luma percentiles (black
level, white level, contrast), the share of pure white and of crushed blacks, warm against cool.
The hue families follow the palette families of references/film-looks.md.

The thresholds are starting values (see THRESHOLDS), not calibrated against real runs yet.
Needs ffmpeg and ffprobe on PATH. Standard library only. Exit code 2 when it cannot run.
"""
import argparse
import colorsys
import json
import math
import shutil
import subprocess
import sys
from pathlib import Path

IMAGE_EXT = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff"}
MAX_SIDE = 160

THRESHOLDS = {
    "colored_sat": 0.15, "colored_val": 0.12,        # a pixel counts as colored above both
    "white_luma": 0.96, "crushed_luma": 0.04,         # pure white, crushed black
    "second_hue_share": 0.25,                         # a second hue needs this share of the top bin
    # delta check (role take): the delta that counts as one full step on each axis
    "step_hue_deg": 60.0, "step_chroma": 0.15, "step_contrast": 0.25, "step_black": 0.12, "step_luma": 0.25,
    "strong": 1.0, "moderate": 0.5,
    # result check (role result): the most an axis may be off
    "ok_hue_deg": 25.0, "ok_chroma": 0.08, "ok_contrast": 0.12, "ok_black": 0.06, "ok_luma": 0.12,
}

# (first degree of the family, name), ascending; red wraps around 0
HUE_NAMES = [(0, "red"), (15, "orange"), (40, "amber"), (60, "yellow"), (75, "lime"), (95, "green"),
             (165, "cyan"), (200, "blue"), (250, "violet"), (285, "magenta"), (325, "pink"), (345, "red")]


def die(msg, code=2):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def run(cmd, binary=False):
    r = subprocess.run(cmd, capture_output=True)
    if not binary:
        r.stdout = r.stdout.decode("utf-8", "replace")
        r.stderr = r.stderr.decode("utf-8", "replace")
    return r


def hue_name(deg):
    deg %= 360
    name = HUE_NAMES[0][1]
    for start, label in HUE_NAMES:
        if deg >= start:
            name = label
    return name


def circ_diff(a, b):
    d = abs(a - b) % 360
    return min(d, 360 - d)


def circ_mean(pairs):
    """Circular mean of (degrees, weight) pairs."""
    sx = sum(w * math.cos(math.radians(h)) for h, w in pairs)
    sy = sum(w * math.sin(math.radians(h)) for h, w in pairs)
    return math.degrees(math.atan2(sy, sx)) % 360 if (sx or sy) else None


# ---------- decoding ----------
def probe(path):
    r = run(["ffprobe", "-v", "error", "-show_entries", "stream=width,height:format=duration", "-of", "json", str(path)])
    if r.returncode:
        die(f"ffprobe failed on {path}: {r.stderr.strip()[:200]}")
    j = json.loads(r.stdout)
    s = next((x for x in j.get("streams", []) if x.get("width")), {})
    try:
        dur = float(j.get("format", {}).get("duration"))
    except (TypeError, ValueError):
        dur = 0.0
    return s.get("width"), s.get("height"), dur


def sample_pixels(path, at, frames):
    """Return a list of (r, g, b) from the sampled frame(s), on a copy no larger than MAX_SIDE."""
    w, h, dur = probe(path)
    if not w or not h:
        die(f"cannot read the size of {path}")
    k = MAX_SIDE / max(w, h)
    tw, th = max(2, round(w * k)), max(2, round(h * k))
    is_image = Path(path).suffix.lower() in IMAGE_EXT
    if is_image or dur <= 0.5:
        times = [None]
    elif at is not None:
        times = [at]
    else:
        times = [dur * f for f in ([0.2, 0.5, 0.8] if frames == 3 else [(i + 1) / (frames + 1) for i in range(frames)])]
    pool = []
    for t in times:
        cmd = ["ffmpeg", "-v", "error"] + (["-ss", f"{t:.3f}"] if t is not None else []) + \
              ["-i", str(path), "-frames:v", "1", "-vf", f"scale={tw}:{th}:flags=area,format=rgb24", "-f", "rawvideo", "-"]
        r = run(cmd, binary=True)
        data = r.stdout
        if len(data) < tw * th * 3:
            continue
        pool.extend(zip(data[0:tw * th * 3:3], data[1:tw * th * 3:3], data[2:tw * th * 3:3]))
    if not pool:
        die(f"could not decode a frame from {path}")
    return pool, len(times)


# ---------- measuring ----------
def measure(pixels):
    T = THRESHOLDS
    n = len(pixels)
    lumas, hs = [], []
    chroma = 0.0
    for r, g, b in pixels:
        y = (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255.0
        h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
        lumas.append(y)
        hs.append((h * 360.0, s, v, y))
        chroma += s * v
    order = sorted(lumas)
    pct = lambda p: order[min(n - 1, max(0, int(round(p / 100.0 * (n - 1)))))]
    p1, p5, p50, p95, p99 = pct(1), pct(5), pct(50), pct(95), pct(99)

    colored = [(h, s, v, y) for h, s, v, y in hs if s >= T["colored_sat"] and v >= T["colored_val"]]
    out = {
        "pixels": n,
        "mean_luma": round(sum(lumas) / n, 3), "black_level": round(p1, 3), "white_level": round(p99, 3),
        "contrast": round(p95 - p5, 3), "median_luma": round(p50, 3),
        "white_pct": round(100.0 * sum(1 for y in lumas if y > T["white_luma"]) / n, 1),
        "crushed_pct": round(100.0 * sum(1 for y in lumas if y < T["crushed_luma"]) / n, 1),
        "chroma": round(chroma / n, 3),
        "colored_share": round(len(colored) / n, 3),
    }
    out["luma_register"] = "low-key" if out["mean_luma"] < 0.30 else ("high-key" if out["mean_luma"] > 0.55 else "mid-key")
    if not colored:
        out.update({"mean_sat": 0.0, "dominant_hue_deg": None, "dominant_name": "neutral", "second_hue_deg": None,
                    "second_name": None, "warm_pct": 0.0, "cool_pct": 0.0, "shadow_hue_deg": None,
                    "highlight_hue_deg": None, "split_deg": None, "saturation_register": "near-neutral"})
        return out

    out["mean_sat"] = round(sum(s for _, s, _, _ in colored) / len(colored), 3)
    bins = [0.0] * 12
    for h, s, v, _ in colored:
        bins[int(((h + 15) % 360) // 30)] += s * v
    total = sum(bins)
    best = max(range(12), key=lambda i: bins[i])
    pairs = []
    for h, s, v, _ in colored:
        b = int(((h + 15) % 360) // 30)
        if min((b - best) % 12, (best - b) % 12) <= 1:
            pairs.append((h, s * v))
    dom = circ_mean(pairs)
    second = None
    rest = [i for i in range(12) if min((i - best) % 12, (best - i) % 12) >= 2 and bins[i] >= T["second_hue_share"] * bins[best]]
    if rest:
        sb = max(rest, key=lambda i: bins[i])
        second = (sb * 30) % 360
    out["dominant_hue_deg"] = round(dom, 1)
    out["dominant_name"] = hue_name(dom)
    out["second_hue_deg"] = second
    out["second_name"] = hue_name(second) if second is not None else None
    out["hue_concentration"] = round(sum(bins[(best + d) % 12] for d in (-1, 0, 1)) / total, 2) if total else 0.0
    warm = sum(w for h, w in ((h, s * v) for h, s, v, _ in colored) if h >= 330 or h < 70)
    cool = sum(w for h, w in ((h, s * v) for h, s, v, _ in colored) if 150 <= h < 270)
    out["warm_pct"], out["cool_pct"] = round(100.0 * warm / total, 1), round(100.0 * cool / total, 1)
    lo_cut, hi_cut = pct(25), pct(75)
    sh = [(h, s * v) for h, s, v, y in colored if y <= lo_cut]
    hi = [(h, s * v) for h, s, v, y in colored if y >= hi_cut]
    sh_h = circ_mean(sh) if len(sh) >= 0.02 * n else None
    hi_h = circ_mean(hi) if len(hi) >= 0.02 * n else None
    out["shadow_hue_deg"] = round(sh_h, 1) if sh_h is not None else None
    out["highlight_hue_deg"] = round(hi_h, 1) if hi_h is not None else None
    out["split_deg"] = round(circ_diff(sh_h, hi_h), 1) if sh_h is not None and hi_h is not None else None
    sat = out["mean_sat"]
    out["saturation_register"] = "near-neutral" if out["colored_share"] < 0.15 else ("muted" if sat < 0.30 else "saturated")
    return out


def describe(m):
    dom = m["dominant_name"]
    if m["dominant_hue_deg"] is not None:
        dom += f" ({m['dominant_hue_deg']:.0f} deg" + (f", then {m['second_name']}" if m["second_name"] else "") + ")"
    split = (f"; shadows hue {m['shadow_hue_deg']:.0f} deg against highlights {m['highlight_hue_deg']:.0f} deg "
             f"(split {m['split_deg']:.0f} deg)") if m.get("split_deg") is not None else ""
    return (f"{m['saturation_register']} {dom}, {m['luma_register']}; chroma {m['chroma']:.2f} "
            f"(colored {100 * m['colored_share']:.0f}% of the frame, mean saturation {m['mean_sat']:.2f}); "
            f"luma mean {m['mean_luma']:.2f}, black level {m['black_level']:.2f}, white level {m['white_level']:.2f}, "
            f"contrast {m['contrast']:.2f}; warm {m['warm_pct']:.0f}% cool {m['cool_pct']:.0f}%{split}; "
            f"pure white {m['white_pct']:.1f}%, crushed {m['crushed_pct']:.1f}%")


# ---------- comparing ----------
def deltas(a, b):
    both_colored = a["dominant_hue_deg"] is not None and b["dominant_hue_deg"] is not None
    return {"hue_deg": round(circ_diff(a["dominant_hue_deg"], b["dominant_hue_deg"]), 1) if both_colored else None,
            "chroma": round(b["chroma"] - a["chroma"], 3), "contrast": round(b["contrast"] - a["contrast"], 3),
            "black_level": round(b["black_level"] - a["black_level"], 3), "mean_luma": round(b["mean_luma"] - a["mean_luma"], 3)}


def delta_check(a, b):
    """Role take: how far is the target look from the take, on each axis, in steps."""
    T, d = THRESHOLDS, deltas(a, b)
    steps = {"hue": (d["hue_deg"] / T["step_hue_deg"]) if d["hue_deg"] is not None else
             (0.0 if a["dominant_hue_deg"] is None and b["dominant_hue_deg"] is None else 1.0),
             "saturation (chroma)": abs(d["chroma"]) / T["step_chroma"], "contrast": abs(d["contrast"]) / T["step_contrast"],
             "black level": abs(d["black_level"]) / T["step_black"], "brightness": abs(d["mean_luma"]) / T["step_luma"]}
    score = max(steps.values())
    lead = sorted(steps, key=lambda k: -steps[k])[:2]
    if score >= T["strong"]:
        status, text = "STRONG", "the target look is far from the take: the before and after will read"
    elif score >= T["moderate"]:
        status, text = "MODERATE", "the target look changes the take, but not by much on any one axis; consider a stronger film of the same palette"
    else:
        status, text = "SOFT", ("the target look barely differs from the take (same hue family, similar saturation, contrast and "
                                "darkness): the before and after will be weak. Warn the user, offer 2 or 3 stronger films of the "
                                "SAME palette family (film-looks.md) and ask")
    return status, text, score, lead, d


def result_check(a, b):
    """Role result: which axes of the generated frame are off from the target, with the reinforcement to try."""
    T, d = THRESHOLDS, deltas(a, b)
    issues = []
    if d["hue_deg"] is not None and d["hue_deg"] > T["ok_hue_deg"]:
        issues.append(f"the dominant hue is {d['hue_deg']:.0f} deg from the target ({a['dominant_name']} against "
                      f"{b['dominant_name']}): restate the palette (axis 3) and which elements carry it")
    if d["chroma"] > T["ok_chroma"]:
        issues.append(f"less colorful than the target (chroma {a['chroma']:.2f} against {b['chroma']:.2f}): a tint, not a look; "
                      "add two more axes from eight-axis.md, usually optics and atmosphere")
    if d["black_level"] < -T["ok_black"]:
        issues.append(f"blacks are higher than the target's (black level {a['black_level']:.2f} against {b['black_level']:.2f}): "
                      "reinforce 'Blacks rich and velvety, never grey'")
    if d["black_level"] > T["ok_black"] or a["crushed_pct"] > b["crushed_pct"] + 15:
        issues.append(f"blacks are crushed (black level {a['black_level']:.2f}, crushed {a['crushed_pct']:.0f}%): reinforce "
                      "'Shadows dense but never fully crushed, with visible detail breathing inside them'")
    if d["contrast"] > T["ok_contrast"]:
        issues.append(f"contrast is lower than the target's ({a['contrast']:.2f} against {b['contrast']:.2f}): reinforce axis 4 "
                      "(dense blacks, protected highlights) and the filmic shoulder")
    if d["contrast"] < -T["ok_contrast"]:
        issues.append(f"contrast is higher than the target's ({a['contrast']:.2f} against {b['contrast']:.2f})")
    if a["white_pct"] > b["white_pct"] + 2.0:
        issues.append(f"pure white survived ({a['white_pct']:.1f}% of the frame against {b['white_pct']:.1f}% in the target): "
                      "reinforce 'No pure white anywhere, every highlight slightly tinted, dimmed'")
    if abs(d["mean_luma"]) > T["ok_luma"]:
        issues.append(f"the frame is {'brighter' if d['mean_luma'] < 0 else 'darker'} than the target (luma mean {a['mean_luma']:.2f} "
                      f"against {b['mean_luma']:.2f}): reinforce axis 6 (exposure)")
    return issues, d


def main():
    ap = argparse.ArgumentParser(description="Measure hue, saturation, black level and contrast of a take and a target look.")
    ap.add_argument("take", type=Path, help="the raw take (video or image), or the generated result with --role result")
    ap.add_argument("target", type=Path, nargs="?", help="a still or a clip of the target film's look")
    ap.add_argument("--at", type=float, help="second to sample in the first video (default: 3 frames at 20, 50 and 80 percent)")
    ap.add_argument("--target-at", type=float, help="second to sample in the target video")
    ap.add_argument("--frames", type=int, default=3, help="frames to sample per video when --at is not given (3)")
    ap.add_argument("--role", choices=["take", "result"], default="take",
                    help="take: judge whether the target look will read; result: compare a generated video with the target")
    ap.add_argument("--json", action="store_true", help="print the measurements as JSON")
    a = ap.parse_args()

    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    for tool in ("ffmpeg", "ffprobe"):
        if not shutil.which(tool):
            die(f"{tool} not found on PATH (run scripts/check_env.py for the install command)")
    for p in (a.take, a.target):
        if p is not None and not p.exists():
            die(f"file not found: {p}")

    first_label = "take" if a.role == "take" else "result"
    px, nf = sample_pixels(a.take, a.at, max(1, a.frames))
    m1 = measure(px)
    m1["file"], m1["frames"] = a.take.name, nf
    report = {first_label: m1}
    lines = [f"{first_label:6s} {a.take.name} ({nf} frame{'s' if nf != 1 else ''}): {describe(m1)}"]
    verdict = None
    if a.target:
        px2, nf2 = sample_pixels(a.target, a.target_at, max(1, a.frames))
        m2 = measure(px2)
        m2["file"], m2["frames"] = a.target.name, nf2
        report["target"] = m2
        lines.append(f"target {a.target.name} ({nf2} frame{'s' if nf2 != 1 else ''}): {describe(m2)}")
        if a.role == "take":
            status, text, score, lead, d = delta_check(m1, m2)
            report["delta"] = {**d, "score": round(score, 2), "verdict": status, "leading_axes": lead}
            hue = f"hue {d['hue_deg']:.0f} deg" if d["hue_deg"] is not None else "hue n/a (a neutral frame)"
            lines.append(f"delta  {hue}, chroma {d['chroma']:+.2f}, contrast {d['contrast']:+.2f}, black level "
                         f"{d['black_level']:+.2f}, luma {d['mean_luma']:+.2f}")
            lines.append(f"DELTA CHECK: {status} (score {score:.2f}; driven by {', '.join(lead)}): {text}")
            verdict = status
        else:
            issues, d = result_check(m1, m2)
            report["delta"] = {**d, "issues": issues}
            hue = f"hue {d['hue_deg']:.0f} deg" if d["hue_deg"] is not None else "hue n/a (a neutral frame)"
            lines.append(f"delta  {hue}, chroma {d['chroma']:+.2f}, contrast {d['contrast']:+.2f}, black level "
                         f"{d['black_level']:+.2f}, luma {d['mean_luma']:+.2f} (target minus result)")
            if issues:
                lines.append(f"RESULT CHECK: {len(issues)} axis(es) off the target")
                lines += [f"  - {i}" for i in issues]
                verdict = "OFF"
            else:
                lines.append("RESULT CHECK: CLOSE to the target on hue, saturation, contrast, black level and brightness")
                verdict = "CLOSE"
    else:
        lines.append("no target given: the numbers above are the take's own look; pass a still of the film to get the delta check")
    if a.json:
        print(json.dumps(report, ensure_ascii=False, indent=1))
    else:
        print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
