#!/usr/bin/env python3
"""Verify a delivered cine-grade DIRECTOR CUT prompt (the default mode) before it goes to the user.

The director cut reuses the cine-multicam camera skeleton and adds a LIGHTING AND COLOR GRADE
section, so cine-multicam's verifier rejects it. This one checks the same kind of structure for
the director cut, with the load-bearing lines read from references/director-cut.md at run time
(one source of truth: change the skeleton there and this follows).

Usage: python verify_director_cut.py <delivered_prompt.txt> [--duration <seconds>]

PASS iff:
  - the seven sections appear in order: CRITICAL, LIGHTING AND COLOR GRADE, CAMERA SEQUENCE,
    CAMERA RHYTHM, REAL CAMERA IMPERFECTIONS, CONTINUITY, FINAL FEEL, with no invented section;
  - every load-bearing sentence of the skeleton is present verbatim (the pronoun, count, color
    and director slots may differ), the closing negatives list included; em and en dashes count
    as spaces when comparing, so a dash never fails a sentence;
  - the grade section is more than a stub;
  - 2 to 8 shot blocks with `MM:SS.d-MM:SS.d  --  NAME` headers (en dash and em dash as in the
    skeleton): ascending, chained, the first at 00:00, the last ending at --duration (within
    0.15 s) when given;
  - "Use N distinct shots" and "Imagine N real cameras" both say the real number of shots;
  - at most one shot marked "noticeably dynamic";
  - no sibling-skill tokens, no robotic-arm noun, no aerial, drone or god's-eye viewpoint.

Warnings (never fail): a shot under about 2 s, equal shot lengths, a shot without an action
anchor ("as he ...", "while she ..."), more than one shot that reads as a dynamic move, an
overhead or top-down shot (check the scale rule), red-flag words in the grade or the shots
("replace", "recolor", "swap the", "add a ..."), no duration given.

Exit 0 on PASS, 1 on FAIL. Standard library only.
"""
import argparse
import re
import sys
from pathlib import Path

TOL = 0.051          # chaining / start-at-zero tolerance (one-decimal timecodes)
DURATION_TOL = 0.15  # last shot end vs the real video duration
MIN_SHOT_WARN = 2.0  # shots under about 2 s read as frenetic, not cinematic
SHOTS_MIN, SHOTS_MAX = 2, 8

EN, EM = chr(0x2013), chr(0x2014)

SECTIONS = ["CRITICAL", "LIGHTING AND COLOR GRADE", "CAMERA SEQUENCE", "CAMERA RHYTHM",
            "REAL CAMERA IMPERFECTIONS", "CONTINUITY", "FINAL FEEL"]
CHECKED_SECTIONS = ["CRITICAL", "LIGHTING AND COLOR GRADE", "CAMERA RHYTHM", "CONTINUITY", "FINAL FEEL"]

# tokens owned by the sibling skills: any of them here means a frankenstein prompt
SIBLING_TOKENS = ["* At [", "From [", "kinetic super", "Kinetic super", "Whip the camera", "Instantly snap",
                  "extreme high angle"]
RIG_NOUNS = ["robot arm", "robotic arm"]  # naming it renders an actual robotic arm into the scene as a prop
# the scale rule: no camera frames the subject smaller than the base video; no aerial or god's-eye viewpoints
AERIAL = re.compile(r"\b(?:aerial|drone|god['" + chr(0x2019) + r"]?s[- ]eye|bird['" + chr(0x2019) + r"]?s[- ]eye|helicopter)\b",
                    re.IGNORECASE)
OVERHEAD = re.compile(r"\b(?:overhead|top[- ]down)\b", re.IGNORECASE)
DYNAMIC_MARK = re.compile(r"noticeably dynamic", re.IGNORECASE)
DYNAMIC_WORDS = re.compile(r"\b(?:whip|snap zoom|crash zoom|fast (?:push|arc|precision|pull|tracking)|"
                           r"precision (?:camera )?move|rapid)\b", re.IGNORECASE)
RED_FLAGS = re.compile(r"\b(?:replace|recolor|swap the|add(?:ed)? (?:a|an|some|new)\b)", re.IGNORECASE)
ANCHOR = re.compile(r"\b(?:as|when|while)\s+(?:he|she|they|his|her|their|the)\b", re.IGNORECASE)
SHOT_HEADER = re.compile(
    r"^(\d{2}):(\d{2}(?:\.\d)?)[-" + EN + r"](\d{2}):(\d{2}(?:\.\d)?)\s+(?:" + EM + r"|--)\s+(.+?)\s*$")
CAPS_HEADER = re.compile(r"^[A-Z][A-Z0-9 \-" + EN + EM + r"&()'/+]{3,50}$")
USE_N = re.compile(r"Use (\d+) distinct shots")
IMAGINE_N = re.compile(r"Imagine (\d+) real cameras")
DURATION_LINE = re.compile(r"The BASE VIDEO is exactly (\d+(?:\.\d+)?) seconds long\.")


def fail(msg):
    print(f"FAIL: {msg}")
    sys.exit(1)


def to_seconds(mm, ss):
    return int(mm) * 60 + float(ss)


def norm(text):
    """Dashes count as spaces and runs of whitespace as one, so a dash never decides a comparison."""
    return re.sub(r"\s+", " ", text.replace(EM, " ").replace(EN, " ")).strip()


def section_of(line):
    for s in SECTIONS:
        if line.startswith(s):
            return s
    return None


def skeleton_rules():
    """Load-bearing sentences from the skeleton in references/director-cut.md, as (section, regex, text).
    Placeholders such as [his], [N], [color] or [Director tone sentence.] become wildcards."""
    ref = Path(__file__).resolve().parent.parent / "references" / "director-cut.md"
    try:
        md = ref.read_text(encoding="utf-8")
    except OSError:
        sys.exit(f"could not read the skeleton from {ref}")
    m = re.search(r"## Skeleton \(validated hybrid.*?\n```\n(.*?)\n```", md, re.S)
    if not m:
        sys.exit("could not extract the skeleton from references/director-cut.md")
    rules, current = [], None
    for raw in m.group(1).split("\n"):
        sec = section_of(raw.strip())
        if sec:
            current = sec
            continue
        if current not in CHECKED_SECTIONS:
            continue
        line = raw.strip()
        if not line:
            continue
        if current == "LIGHTING AND COLOR GRADE":
            # only the closing sentences of the grade paragraph are load-bearing
            pos = line.find("The grade is locked")
            if pos < 0:
                continue
            line = line[pos:]
        tokens = []

        def stash(mo):
            tokens.append(mo.group(0))
            return f"\x00{len(tokens) - 1}\x00"

        line = re.sub(r"\[[^\]]*\]", stash, line)
        for sent in re.split(r"(?<=[.!?])\s+", norm(line)):
            sent = sent.strip()
            body = re.sub(r"\x00\d+\x00", "", sent).strip()
            if len(body.split()) < 3:
                continue
            pattern = re.escape(sent)
            pattern = re.sub(r"\\?\x00\d+\\?\x00", ".*?", pattern)
            rules.append((current, re.compile(pattern), re.sub(r"\x00\d+\x00", "[...]", sent)))
    return rules


def main():
    ap = argparse.ArgumentParser(description="Structural verifier for cine-grade director-cut prompts")
    ap.add_argument("prompt", type=Path)
    ap.add_argument("--duration", type=float, help="real video duration in seconds (from ffprobe or beats.py)")
    args = ap.parse_args()
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    text = args.prompt.read_text(encoding="utf-8-sig").replace("\r\n", "\n")
    lines = text.split("\n")
    low = text.lower()

    for tok in SIBLING_TOKENS:
        if tok in text:
            fail(f"sibling-skill token found: {tok!r}: the cine-multicam, kinetic and multicam templates must never "
                 f"be mixed into a director cut")
    for noun in RIG_NOUNS:
        if noun in low:
            fail(f"robotic-arm noun found: {noun!r}: naming it renders an actual robotic arm into the scene as a prop; "
                 f"write 'a precision camera move' and describe the trajectory")

    positions = {}
    for i, line in enumerate(lines):
        s = section_of(line)
        if s and s not in positions:
            positions[s] = i
    for s in SECTIONS:
        if s not in positions:
            fail(f"missing required section: {s}")
    order = [positions[s] for s in SECTIONS]
    if order != sorted(order):
        fail(f"sections out of order (expected {', '.join(SECTIONS)})")

    for line in lines:
        s = line.strip()
        if not s or SHOT_HEADER.match(s) or section_of(s):
            continue
        if CAPS_HEADER.match(s) and not any(c.islower() for c in s):
            fail(f"unknown section header {s!r}: the director cut has no such section. Never paste the spoken "
                 f"dialogue or a transcript into the prompt")

    flat = norm(text)
    if not flat.startswith("Edit the attached BASE VIDEO."):
        fail("the prompt must open with: Edit the attached BASE VIDEO.")
    for sec, rx, sentence in skeleton_rules():
        if not rx.search(flat):
            fail(f"load-bearing line missing or changed in {sec}: {sentence!r} (reproduce the skeleton lines "
                 f"verbatim; only the pronoun, count, color and director slots change)")

    bounds = [positions[s] for s in SECTIONS] + [len(lines)]
    body_of = {s: "\n".join(lines[bounds[i] + 1:bounds[i + 1]]) for i, s in enumerate(SECTIONS)}
    grade_words = len(body_of["LIGHTING AND COLOR GRADE"].split())
    if grade_words < 40:
        fail(f"the LIGHTING AND COLOR GRADE section is a stub ({grade_words} words): write the 8-axis treatment "
             f"onto the real elements of the frame")

    shots, current = [], None
    for line in lines[positions["CAMERA SEQUENCE"] + 1:positions["CAMERA RHYTHM"]]:
        m = SHOT_HEADER.match(line.strip())
        if m:
            if current:
                shots.append(current)
            current = [to_seconds(m.group(1), m.group(2)), to_seconds(m.group(3), m.group(4)), m.group(5), ""]
        elif current is not None:
            current[3] += line + "\n"
    if current:
        shots.append(current)
    if not shots:
        fail("no shot blocks found under CAMERA SEQUENCE (headers must look like `00:04.2" + EN + "00:07.6 " + EM +
             " SHOT NAME`)")
    if not SHOTS_MIN <= len(shots) <= SHOTS_MAX:
        fail(f"shot count {len(shots)} outside the {SHOTS_MIN}-{SHOTS_MAX} range")
    if abs(shots[0][0]) > TOL:
        fail(f"first shot must start at 00:00, not {shots[0][0]:.1f}s")
    for i, (start, end, name, _) in enumerate(shots, 1):
        if not start < end:
            fail(f"shot {i} ({name}) range is not ascending: {start:.1f} -> {end:.1f}")
    for i in range(len(shots) - 1):
        if abs(shots[i][1] - shots[i + 1][0]) > TOL:
            fail(f"shots {i + 1} and {i + 2} do not chain ({shots[i][1]:.1f} vs {shots[i + 1][0]:.1f}): every cut "
                 f"point must be shared by the shots on both sides")
    if args.duration is not None and abs(shots[-1][1] - args.duration) > DURATION_TOL:
        fail(f"last shot ends at {shots[-1][1]:.1f}s but the video duration is {args.duration:.1f}s: the timecodes "
             f"must sum to the full duration")

    for label, rx in (("Use N distinct shots", USE_N), ("Imagine N real cameras", IMAGINE_N)):
        m = rx.search(text)
        if m and int(m.group(1)) != len(shots):
            fail(f"{label!r} says {m.group(1)} but the sequence has {len(shots)} shots")
    dm = DURATION_LINE.search(text)
    if dm and args.duration is not None and abs(float(dm.group(1)) - args.duration) > DURATION_TOL:
        fail(f"the prompt declares the video as {dm.group(1)}s but the real duration is {args.duration:.1f}s")

    marked = [i + 1 for i, (_, _, name, body) in enumerate(shots) if DYNAMIC_MARK.search(name + " " + body)]
    if len(marked) > 1:
        fail(f"more than one dynamic-surprise shot (shots {marked}): at most one dynamic move per director cut")
    for scope in ("LIGHTING AND COLOR GRADE", "CAMERA SEQUENCE", "CAMERA RHYTHM"):
        m = AERIAL.search(body_of[scope])
        if m:
            fail(f"{m.group(0)!r} in {scope}: the scale rule bans aerial, drone and god's-eye viewpoints (a "
                 f"dot-sized subject flips the model into pure generation and the clip comes back stiff and plastic)")

    warnings = []
    durations = [round(end - start, 1) for start, end, _, _ in shots]
    if len(shots) > 2 and len(set(durations)) == 1:
        warnings.append(f"all {len(shots)} shots have the same length ({durations[0]}s): the rhythm rule asks for "
                        f"uneven durations")
    for i, (start, end, name, body) in enumerate(shots, 1):
        if end - start < MIN_SHOT_WARN - 0.05:
            warnings.append(f"shot {i} ({name}) runs only {end - start:.1f}s: under about {MIN_SHOT_WARN:.0f}s a shot "
                            f"reads as frenetic unless the take is short and the grammar asks for it")
        if not ANCHOR.search(body):
            warnings.append(f"shot {i} ({name}) has no action anchor ('as he...', 'while she...'): double-anchoring "
                            f"the timecode to an action makes the cut land better")
        if OVERHEAD.search(name + " " + body):
            warnings.append(f"shot {i} ({name}) is overhead or top-down: check the scale rule (the subject must not "
                            f"be smaller than in the base video)")
    dyn = [i + 1 for i, (_, _, name, body) in enumerate(shots) if DYNAMIC_WORDS.search(name + " " + body)]
    if len(dyn) > 1:
        warnings.append(f"shots {dyn} read as dynamic moves (whip, crash zoom, fast push, precision move): the "
                        f"contrast rule allows one")
    for scope in ("LIGHTING AND COLOR GRADE", "CAMERA SEQUENCE"):
        for m in RED_FLAGS.finditer(body_of[scope]):
            warnings.append(f"red-flag wording in {scope}: {m.group(0)!r}: rewrite it as what the surface BECOMES "
                            f"under the light, never as a replacement or an addition")
    if args.duration is None:
        warnings.append("no --duration given: the end of the last shot was not checked against the video")

    print("PASS: director-cut structure holds")
    print(f"shots: {len(shots)}, total {shots[-1][1]:.1f}s"
          + (f" (video {args.duration:.1f}s)" if args.duration is not None else "") + f", durations {durations}")
    for i, (start, end, name, _) in enumerate(shots, 1):
        print(f"  {i}. {start:5.1f} -> {end:5.1f}  ({end - start:3.1f}s)  {name}")
    for w in warnings:
        print(f"WARNING: {w}")
    sys.exit(0)


if __name__ == "__main__":
    main()
