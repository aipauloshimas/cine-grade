#!/usr/bin/env python3
"""Verify delivered cine-grade DIRECTOR CUT prompts (the default mode) before they go to the user.

The director cut reuses the cine-multicam camera skeleton and adds a LIGHTING AND COLOR GRADE
section, so cine-multicam's verifier rejects it. This one checks the same kind of structure for
the director cut, with the load-bearing lines read from references/director-cut.md at run time
(one source of truth: change the skeleton there and this follows) and the director grammars read
from references/directors.json.

Usage:
  python verify_director_cut.py <prompt.txt> [more.txt ...] [--duration <seconds>] [--silent]
                                [--director "<name>"]
  python verify_director_cut.py --print-table      (director table for director-cut.md, from directors.json)

PASS (per file) iff:
  - the seven sections appear in order: CRITICAL, LIGHTING AND COLOR GRADE, CAMERA SEQUENCE,
    CAMERA RHYTHM, REAL CAMERA IMPERFECTIONS, CONTINUITY, FINAL FEEL, with no invented section;
  - every load-bearing sentence of the skeleton is present verbatim (the pronoun, count, color
    and director slots may differ), the closing negatives list included; em and en dashes count
    as spaces when comparing, so a dash never fails a sentence. With --silent, the speech lines
    are replaced by the silent lines listed in director-cut.md ("Silent clip");
  - no generic wording: "one continuous take", "single take", "single continuous", "no cut(s)",
    "uninterrupted take", "machine...", "robot...". A director cut is 2 or more shots joined by
    clean hard cuts, in the director's own camera grammar, never one take and never a generic move;
  - the grade section is more than a stub;
  - 2 to 8 shot blocks with `MM:SS.d-MM:SS.d  --  NAME` headers (en dash and em dash as in the
    skeleton): ascending, chained, the first at 00:00, the last ending at --duration (within
    0.15 s) when given;
  - CAMERA RHYTHM says "Use N distinct shots" and CONTINUITY "Imagine N real cameras", N = the
    real number of shots;
  - when the director is known (--director, or named in FINAL FEEL and present in directors.json),
    no shot uses a move listed in that director's `never`;
  - at most one shot marked "noticeably dynamic";
  - no sibling-skill tokens, no robotic-arm noun, no aerial, drone or god's-eye viewpoint.

Warnings (never fail): FINAL FEEL names no director; a director is not in directors.json (derive
its grammar with the six-point method and tag derived moves); a shot uses none of the director's
`moves` and is not tagged `(derived: <reason>)`; a shot under about 2 s; equal shot lengths; a shot
without an action anchor ("as he ...", "while she ..."); more than one shot that reads as a dynamic
move; an overhead or top-down shot (check the scale rule); red-flag words in the grade or the
shots ("replace", "recolor", "swap the", "add a ..."); no duration given; with --silent, no
"silent action" line or a shot that talks about speech.

Batch mode (two or more files): besides the per-file checks, the CAMERA SEQUENCE sections are
compared pairwise and a WARNING is printed for every pair that is near-identical (the same camera
move written for two different films). Exit 0 when every file passes, 1 when any fails.
Standard library only.
"""
import argparse
import json
import re
import sys
from itertools import combinations
from pathlib import Path

TOL = 0.051          # chaining / start-at-zero tolerance (one-decimal timecodes)
DURATION_TOL = 0.15  # last shot end vs the real video duration
MIN_SHOT_WARN = 2.0  # shots under about 2 s read as frenetic, not cinematic
SHOTS_MIN, SHOTS_MAX = 2, 8

# Camera-section similarity (batch mode). Jaccard index of the camera-vocabulary word sets of two CAMERA
# SEQUENCE sections (see camera_words: content words, 5-letter stems, minus the room's own words from the
# same prompt's CRITICAL section). Measured on two sets of six to seven prompts for one and the same clip:
# single-take prompts that all open "slow push, then a still hold, same take" scored up to 0.33 pairwise
# (0.29 and 0.33 for the two closest pairs); director-cut prompts written from seven different directors'
# grammars scored 0.06-0.23; two versions of the same film's cut scored 0.96. 0.26 sits between the
# groups. It is a heuristic: it catches copied or lightly reworded camera sections, not two different words
# for the same move, so the checkpoint's source column (SKILL.md red flags) stays the real defence.
SIMILARITY_WARN = 0.26

EN, EM = chr(0x2013), chr(0x2014)

SECTIONS = ["CRITICAL", "LIGHTING AND COLOR GRADE", "CAMERA SEQUENCE", "CAMERA RHYTHM",
            "REAL CAMERA IMPERFECTIONS", "CONTINUITY", "FINAL FEEL"]
CHECKED_SECTIONS = ["CRITICAL", "LIGHTING AND COLOR GRADE", "CAMERA RHYTHM", "CONTINUITY", "FINAL FEEL"]

# tokens owned by the sibling skills: any of them here means a frankenstein prompt
SIBLING_TOKENS = ["* At [", "From [", "kinetic super", "Kinetic super", "Whip the camera", "Instantly snap",
                  "extreme high angle"]
RIG_NOUNS = ["robot arm", "robotic arm"]  # naming it renders an actual robotic arm into the scene as a prop

# Generic / single-take wording that means the prompt is not a real director cut. "uninterrupted
# performance" (the skeleton's CRITICAL line) is deliberately NOT matched by any of these.
GENERIC_WORDING = [
    (re.compile(r"\bone continuous take\b|\bsingle continuous\b|\bsingle take\b|\buninterrupted take\b|"
                r"\bno cuts?\b", re.IGNORECASE),
     "single-take wording: a director cut is 2 or more shots joined by clean hard cuts, even for a clip without "
     "speech (cut on action beats: see 'Silent clip' in references/director-cut.md). Rewrite it as separate shot "
     "blocks, each with its own camera"),
    (re.compile(r"\bmachine\w*|\brobot\w*", re.IGNORECASE),
     "generic camera wording ('machine precision', 'robotic'): it is the same move for every film and, for "
     "'robot', renders a prop. Describe the move the director would actually use (see references/directors.json) "
     "instead. If 'machine' names a real object in the room, call it by its specific name"),
]
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
DERIVED_TAG = re.compile(r"\(derived:\s*[^)]+\)", re.IGNORECASE)
NO_SPEECH = re.compile(r"\b(?:no speech|silent|wordless|no audio)\b", re.IGNORECASE)
SPEECH_IN_SHOT = re.compile(r"\b(?:says|said|speaks|speaking|spoken|his line|her line|dialogue|lip[- ]sync)\b",
                            re.IGNORECASE)
NEGATOR = re.compile(r"\b(?:no|never|not|without|nor|neither|avoid\w*|zero)\b", re.IGNORECASE)
STOPWORDS = set("""about above after again against along also among and any around away back been before being below
between both camera cameras cannot could does doing down during each ever every face first from frame frames further
have having here himself herself into itself just keep keeps like made make more most much must never only other over
same shot shots some such than that their them then there these they this those through under until upon very were what
when where which while will with within without would your clean hard cut cuts identical grade""".split())


class Fail(Exception):
    pass


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


def skill_root():
    return Path(__file__).resolve().parent.parent


def read_ref(name):
    ref = skill_root() / "references" / name
    try:
        return ref.read_text(encoding="utf-8")
    except OSError:
        sys.exit(f"could not read {ref}: run the verifier from a complete copy of the cine-grade skill")


def compile_sentence(sent):
    """A skeleton sentence (placeholders like [his], [N] or [color] become wildcards) -> (regex, display)."""
    tokens = []

    def stash(mo):
        tokens.append(mo.group(0))
        return f"\x00{len(tokens) - 1}\x00"

    sent = norm(re.sub(r"\[[^\]]*\]", stash, sent))
    pattern = re.escape(sent)
    pattern = re.sub(r"\\?\x00\d+\\?\x00", ".*?", pattern)
    return re.compile(pattern), re.sub(r"\x00\d+\x00", "[...]", sent)


def skeleton_rules():
    """Load-bearing sentences from the skeleton in references/director-cut.md, as (section, regex, display)."""
    md = read_ref("director-cut.md")
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
        line = re.sub(r"\[[^\]]*\]", lambda mo: "\x01" * len(mo.group(0)), line)  # keep sentence splits off slots
        line = re.sub(r"\x01+", lambda mo: "[x]", line)
        for sent in re.split(r"(?<=[.!?])\s+", norm(line)):
            sent = sent.strip()
            if len(re.sub(r"\[[^\]]*\]", "", sent).split()) < 3:
                continue
            rx, display = compile_sentence(sent)
            rules.append((current, rx, display))
    return rules


def silent_pairs():
    """(speech sentence, silent sentence) pairs from the 'Silent clip' block of references/director-cut.md."""
    md = read_ref("director-cut.md")
    m = re.search(r"### Silent clip.*?\n```\n(.*?)\n```", md, re.S)
    if not m:
        sys.exit("could not extract the silent lines from references/director-cut.md ('Silent clip' block)")
    pairs, speech = [], None
    for raw in m.group(1).split("\n"):
        line = raw.strip()
        if line.startswith("speech:"):
            speech = line[len("speech:"):].strip()
        elif line.startswith("silent:") and speech is not None:
            pairs.append((speech, line[len("silent:"):].strip()))
            speech = None
    if not pairs:
        sys.exit("the 'Silent clip' block in references/director-cut.md has no speech:/silent: pairs")
    return pairs


def rules_for(silent):
    rules = skeleton_rules()
    if not silent:
        return rules
    swaps = {}
    for speech, quiet in silent_pairs():
        key = compile_sentence(speech)[1]
        swaps[key] = compile_sentence(quiet)
    out, used = [], set()
    for sec, rx, display in rules:
        if display in swaps:
            used.add(display)
            out.append((sec, *swaps[display]))
        else:
            out.append((sec, rx, display))
    stale = set(swaps) - used
    if stale:
        sys.exit("the 'Silent clip' block in director-cut.md no longer matches the skeleton: "
                 + "; ".join(sorted(stale)))
    return out


def load_directors():
    try:
        data = json.loads(read_ref("directors.json"))
    except ValueError as e:
        sys.exit(f"references/directors.json is not valid JSON: {e}")
    return data["directors"]


def print_table(directors):
    print("| Director / film | Camera grammar | Cut count | Never |")
    print("|---|---|---|---|")
    for d in directors:
        films = ", ".join(d.get("films", []))
        print(f"| **{d['name']}** ({films}) | {d.get('notes', '')} | {d.get('cuts', '')} | "
              f"{', '.join(d.get('never', []))} |")


def kw_hits(keywords, text):
    """Keywords found in text by word prefix, case-insensitive, as (keyword, position of the match)."""
    hits = []
    for kw in keywords:
        for m in re.finditer(r"(?<![\w-])" + re.escape(kw.lower()), text):
            hits.append((kw, m.start()))
    return hits


def negated(text, pos):
    """True when a negator sits shortly before pos in the same sentence ('no handheld', 'never a drift')."""
    start = max(text.rfind(".", 0, pos), text.rfind(";", 0, pos), pos - 40)
    return bool(NEGATOR.search(text[start + 1:pos]))


def find_director(directors, final_feel, wanted):
    """-> (director row or None, name used or None)."""
    def match(name):
        n = name.strip().lower()
        for d in directors:
            if n == d["name"].lower() or n in [a.lower() for a in d.get("aliases", [])]:
                return d
        for d in directors:
            if any(re.search(r"\b" + re.escape(a.lower()) + r"\b", n) for a in d.get("aliases", [])):
                return d
        return None

    if wanted:
        return match(wanted), wanted
    best = None
    for d in directors:
        for a in d.get("aliases", []):
            m = re.search(r"(?<!\w)" + re.escape(a) + r"(?!\w)", final_feel, re.IGNORECASE)
            if m and (best is None or m.start() < best[0]):
                best = (m.start(), d)
    if best:
        return best[1], best[1]["name"]
    for m in re.finditer(r"(?<=[a-z,] )[A-Z][\w\u00c0-\u017f.-]+(?: [A-Z][\w\u00c0-\u017f.-]+)*", final_feel):
        if "grammar" in final_feel[m.end():m.end() + 70].lower():
            return None, m.group(0)
    return None, None


def content_words(text):
    words = set()
    for w in re.findall(r"[a-z][a-z-]{3,}", text.lower()):
        if w not in STOPWORDS:
            words.add(w[:5])  # crude stem: dolly/dollying, circle/circles/circling share a prefix
    return words


def section_text(text, start, end):
    """Text between a section header line and the next one (empty when the section is missing)."""
    m = re.search(r"^" + start + r"[^" + chr(10) + r"]*" + chr(10) + r"(.*?)^" + end, text, re.S | re.M)
    return m.group(1) if m else ""


def camera_words(text):
    """Content words of the CAMERA SEQUENCE minus the room's own vocabulary (every word that the same prompt's
    LIGHTING AND COLOR GRADE or CRITICAL sections already use: furniture, garments, colors, the action beats).
    What is left is camera vocabulary: the moves, framings and lens words that a director's grammar decides."""
    text = text.replace(chr(13) + chr(10), chr(10))
    camera = content_words(section_text(text, "CAMERA SEQUENCE", "CAMERA RHYTHM"))
    room = content_words(section_text(text, "CRITICAL", "CAMERA SEQUENCE"))
    return camera - room


def jaccard(a, b):
    return len(a & b) / len(a | b) if a | b else 0.0


def verify(path, args, directors, rules):
    """Check one prompt. Returns the report lines; raises Fail with one message."""
    text = path.read_text(encoding="utf-8-sig").replace("\r\n", "\n")
    lines = text.split("\n")
    low = text.lower()
    silent_hint = ("" if args.silent or not NO_SPEECH.search(text) else
                   " (this prompt says the clip has no speech: run with --silent, which checks the silent lines "
                   "from 'Silent clip' in references/director-cut.md instead of the speech lines)")

    for tok in SIBLING_TOKENS:
        if tok in text:
            raise Fail(f"sibling-skill token found: {tok!r}: the cine-multicam, kinetic and multicam templates must "
                       f"never be mixed into a director cut")
    for noun in RIG_NOUNS:
        if noun in low:
            raise Fail(f"robotic-arm noun found: {noun!r}: naming it renders an actual robotic arm into the scene as "
                       f"a prop; write 'a precision camera move' and describe the trajectory")
    for rx, why in GENERIC_WORDING:
        found = sorted({m.group(0).lower() for m in rx.finditer(text)})
        if found:
            raise Fail(f"{', '.join(repr(f) for f in found)} found: {why}")

    positions = {}
    for i, line in enumerate(lines):
        s = section_of(line)
        if s and s not in positions:
            positions[s] = i
    for s in SECTIONS:
        if s not in positions:
            raise Fail(f"missing required section: {s}")
    order = [positions[s] for s in SECTIONS]
    if order != sorted(order):
        raise Fail(f"sections out of order (expected {', '.join(SECTIONS)})")

    for line in lines:
        s = line.strip()
        if not s or SHOT_HEADER.match(s) or section_of(s):
            continue
        if CAPS_HEADER.match(s) and not any(c.islower() for c in s):
            raise Fail(f"unknown section header {s!r}: the director cut has no such section. Never paste the spoken "
                       f"dialogue or a transcript into the prompt")

    flat = norm(text)
    if not flat.startswith("Edit the attached BASE VIDEO."):
        raise Fail("the prompt must open with: Edit the attached BASE VIDEO.")
    for sec, rx, sentence in rules:
        if not rx.search(flat):
            raise Fail(f"load-bearing line missing or changed in {sec}: {sentence!r} (reproduce the skeleton lines "
                       f"verbatim; only the pronoun, count, color and director slots change){silent_hint}")

    bounds = [positions[s] for s in SECTIONS] + [len(lines)]
    body_of = {s: "\n".join(lines[bounds[i] + 1:bounds[i + 1]]) for i, s in enumerate(SECTIONS)}
    grade_words = len(body_of["LIGHTING AND COLOR GRADE"].split())
    if grade_words < 40:
        raise Fail(f"the LIGHTING AND COLOR GRADE section is a stub ({grade_words} words): write the 8-axis "
                   f"treatment onto the real elements of the frame")

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
        raise Fail("no shot blocks found under CAMERA SEQUENCE (headers must look like `00:04.2" + EN + "00:07.6 " +
                   EM + " SHOT NAME`)")
    if not SHOTS_MIN <= len(shots) <= SHOTS_MAX:
        raise Fail(f"shot count {len(shots)} outside the {SHOTS_MIN}-{SHOTS_MAX} range: a director cut is "
                   f"{SHOTS_MIN} or more shots joined by clean hard cuts, never one take")
    if abs(shots[0][0]) > TOL:
        raise Fail(f"first shot must start at 00:00, not {shots[0][0]:.1f}s")
    for i, (start, end, name, _) in enumerate(shots, 1):
        if not start < end:
            raise Fail(f"shot {i} ({name}) range is not ascending: {start:.1f} -> {end:.1f}")
    for i in range(len(shots) - 1):
        if abs(shots[i][1] - shots[i + 1][0]) > TOL:
            raise Fail(f"shots {i + 1} and {i + 2} do not chain ({shots[i][1]:.1f} vs {shots[i + 1][0]:.1f}): every "
                       f"cut point must be shared by the shots on both sides")
    if args.duration is not None and abs(shots[-1][1] - args.duration) > DURATION_TOL:
        raise Fail(f"last shot ends at {shots[-1][1]:.1f}s but the video duration is {args.duration:.1f}s: the "
                   f"timecodes must sum to the full duration")

    m = USE_N.search(body_of["CAMERA RHYTHM"])
    if not m:
        raise Fail(f"CAMERA RHYTHM must say 'Use {len(shots)} distinct shots' (N = the number of shot blocks)")
    if int(m.group(1)) != len(shots):
        raise Fail(f"'Use N distinct shots' says {m.group(1)} but the sequence has {len(shots)} shots")
    m = IMAGINE_N.search(text)
    if m and int(m.group(1)) != len(shots):
        raise Fail(f"'Imagine N real cameras' says {m.group(1)} but the sequence has {len(shots)} shots")
    dm = DURATION_LINE.search(text)
    if dm and args.duration is not None and abs(float(dm.group(1)) - args.duration) > DURATION_TOL:
        raise Fail(f"the prompt declares the video as {dm.group(1)}s but the real duration is {args.duration:.1f}s")

    marked = [i + 1 for i, (_, _, name, body) in enumerate(shots) if DYNAMIC_MARK.search(name + " " + body)]
    if len(marked) > 1:
        raise Fail(f"more than one dynamic-surprise shot (shots {marked}): at most one dynamic move per director cut")
    for scope in ("LIGHTING AND COLOR GRADE", "CAMERA SEQUENCE", "CAMERA RHYTHM"):
        m = AERIAL.search(body_of[scope])
        if m:
            raise Fail(f"{m.group(0)!r} in {scope}: the scale rule bans aerial, drone and god's-eye viewpoints (a "
                       f"dot-sized subject flips the model into pure generation and the clip comes back stiff and "
                       f"plastic)")

    warnings = []
    director, dname = find_director(directors, body_of["FINAL FEEL"], args.director)
    if director is None:
        if dname:
            warnings.append(f"director not in directors.json ({dname}): derive its grammar with the six-point method "
                            f"and tag derived moves with '(derived: <reason>)' (see 'Director not in the table' in "
                            f"references/director-cut.md); no move was checked against a grammar")
        else:
            warnings.append("FINAL FEEL names no director: write the tone sentence in the director's name "
                            "(\"... in Refn's grammar: ...\") so the grammar behind the shots is checkable")
    else:
        for i, (_, _, name, body) in enumerate(shots, 1):
            shot_low = (name + "\n" + body).lower()
            bad = [kw for kw, pos in kw_hits(director.get("never", []), shot_low) if not negated(shot_low, pos)]
            if bad:
                raise Fail(f"shot {i} ({name}) uses {', '.join(repr(b) for b in sorted(set(bad)))}, which "
                           f"is on the 'never' list of {director['name']} in directors.json. Replace the move with "
                           f"one of: {', '.join(director.get('moves', [])[:8])}; or, if the take really needs it, "
                           f"pick another director")
            if not kw_hits(director.get("moves", []), shot_low) and not DERIVED_TAG.search(name + "\n" + body):
                warnings.append(f"shot {i} ({name}) uses none of {director['name']}'s known moves "
                                f"({', '.join(director.get('moves', [])[:6])}, ...): use one, or tag the shot "
                                f"'(derived: <reason>)' and list its source in the checkpoint")

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
        if args.silent and SPEECH_IN_SHOT.search(name + " " + body):
            warnings.append(f"shot {i} ({name}) talks about speech ({SPEECH_IN_SHOT.search(name + ' ' + body).group(0)!r}) "
                            f"but the clip is silent: anchor the shot to an action beat instead")
    dyn = [i + 1 for i, (_, _, name, body) in enumerate(shots) if DYNAMIC_WORDS.search(name + " " + body)]
    if len(dyn) > 1:
        warnings.append(f"shots {dyn} read as dynamic moves (whip, crash zoom, fast push, precision move): the "
                        f"contrast rule allows one")
    for scope in ("LIGHTING AND COLOR GRADE", "CAMERA SEQUENCE"):
        for m in RED_FLAGS.finditer(body_of[scope]):
            warnings.append(f"red-flag wording in {scope}: {m.group(0)!r}: rewrite it as what the surface BECOMES "
                            f"under the light, never as a replacement or an addition")
    if args.silent and not re.search(r"silent action", body_of["CRITICAL"], re.IGNORECASE):
        warnings.append("no 'The silent action, exactly as in the base video: ...' line in CRITICAL: list the action "
                        "beats with their times so the cuts have something to land on")
    if args.duration is None:
        warnings.append("no --duration given: the end of the last shot was not checked against the video")

    out = ["PASS: director-cut structure holds" + (" (silent clip)" if args.silent else "")]
    out.append(f"shots: {len(shots)}, total {shots[-1][1]:.1f}s"
               + (f" (video {args.duration:.1f}s)" if args.duration is not None else "") + f", durations {durations}")
    if director:
        out.append(f"director: {director['name']} (cuts: {director.get('cuts', '?')})")
    for i, (start, end, name, _) in enumerate(shots, 1):
        out.append(f"  {i}. {start:5.1f} -> {end:5.1f}  ({end - start:3.1f}s)  {name}")
    out += [f"WARNING: {w}" for w in warnings]
    return out


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    ap = argparse.ArgumentParser(description="Structural verifier for cine-grade director-cut prompts")
    ap.add_argument("prompts", nargs="*", type=Path, help="one prompt file, or several for batch mode")
    ap.add_argument("--duration", type=float, help="real video duration in seconds (from ffprobe or beats.py)")
    ap.add_argument("--silent", action="store_true",
                    help="the clip has no speech: check the silent lines from director-cut.md 'Silent clip'")
    ap.add_argument("--director", help="director name or alias (default: read from FINAL FEEL); "
                                       "with several files it applies to all of them")
    ap.add_argument("--show-similarity", action="store_true", help="batch mode: print every pairwise score")
    ap.add_argument("--print-table", action="store_true", help="print the director table built from directors.json")
    args = ap.parse_args()

    directors = load_directors()
    if args.print_table:
        print_table(directors)
        return
    if not args.prompts:
        ap.error("give at least one prompt file (or --print-table)")
    rules = rules_for(args.silent)

    failed, cameras = 0, {}
    for path in args.prompts:
        try:
            cameras[path.name] = camera_words(path.read_text(encoding="utf-8-sig"))
        except OSError:
            pass
        if len(args.prompts) > 1:
            print(f"== {path.name}")
        try:
            out = verify(path, args, directors, rules)
        except Fail as e:
            failed += 1
            print(f"FAIL: {e}")
            continue
        except OSError as e:
            failed += 1
            print(f"FAIL: could not read {path}: {e}")
            continue
        print("\n".join(out))

    if len(cameras) > 1:
        sets = cameras
        print("== batch check: CAMERA SEQUENCE similarity")
        flagged = 0
        for (na, a), (nb, b) in combinations(sets.items(), 2):
            j = jaccard(a, b)
            if args.show_similarity:
                print(f"  similarity {j:.2f}  {na} <-> {nb}")
            if j >= SIMILARITY_WARN:
                flagged += 1
                print(f"WARNING: camera sections of {na} and {nb} are near-identical (similarity {j:.2f} >= "
                      f"{SIMILARITY_WARN:.2f}): two films must not share the same camera move or sequence. Rewrite "
                      f"one from its own director's grammar (references/directors.json)")
        if not flagged:
            print(f"ok: no two camera sections are near-identical (threshold {SIMILARITY_WARN:.2f})")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
