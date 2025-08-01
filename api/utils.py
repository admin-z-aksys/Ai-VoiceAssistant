import numpy as np
import random

PHONEME_TO_MORPH_MAP = {
    "AA": "mouthOpen", "AE": "mouthOpen", "AH": "mouthOpen",
    "AO": "mouthOpen", "AW": "mouthOpen", "AY": "mouthOpen",
    "B": "mouthClosed", "CH": "mouthTight", "D": "mouthWide",
    "DH": "mouthOpen", "EH": "mouthSmile", "ER": "mouthRound",
    "EY": "mouthSmile", "F": "mouthBite", "G": "mouthMid",
    "HH": "mouthOpen", "IH": "mouthNarrow", "IY": "mouthNarrow",
    "JH": "mouthTight", "K": "mouthMid", "L": "mouthSmile",
    "M": "mouthClosed", "N": "mouthWide", "NG": "mouthMid",
    "OW": "mouthRound", "OY": "mouthRound", "P": "mouthClosed",
    "R": "mouthRound", "S": "mouthWide", "SH": "mouthTight",
    "T": "mouthWide", "TH": "mouthOpen", "UH": "mouthOpen",
    "UW": "mouthRound", "V": "mouthBite", "W": "mouthRound",
    "Y": "mouthNarrow", "Z": "mouthWide", "ZH": "mouthTight"
}

FALLBACK_MORPHS = {
    "mouthWide": ["mouthMid", "mouthOpen"],
    "mouthClosed": ["mouthBite"],
    "mouthOpen": ["mouthRound", "mouthMid"],
    "mouthTight": ["mouthMid"],
    "mouthRound": ["mouthOpen"],
    "mouthMid": ["mouthWide"],
    "mouthBite": ["mouthClosed"]
}

MAX_MORPH_WEIGHT = 1
MIN_MORPH_WEIGHT = 0
MIN_GAP = 0.03
JITTER_PROB = 0.25
IDLE_FILLER_WEIGHT = 0.2

def generate_morph_targets_from_phonemes(phonemes, steps=100, fade_duration=0.05):
    morph_targets = []
    prev_end = 0.0
    prev_morph = None

    for i, p in enumerate(phonemes):
        char = p.get("char", "").upper()
        start = round(p.get("start", 0), 3)
        end = round(p.get("end", 0), 3)
        duration = end - start

        if duration <= 0 or char not in PHONEME_TO_MORPH_MAP:
            continue

        morph = PHONEME_TO_MORPH_MAP[char]

        # Avoid exact repeat
        if prev_morph == morph:
            fallback = FALLBACK_MORPHS.get(morph)
            if fallback:
                morph = random.choice(fallback + [morph])

        # Insert idle filler if large gap
        gap = start - prev_end
        if gap > 0.3:
            morph_targets.append({
                "morph": "mouthOpen",
                "start": round(prev_end, 3),
                "end": round(start - MIN_GAP, 3),
                "weight": IDLE_FILLER_WEIGHT,
                "fade_in": 0.03,
                "fade_out": 0.03
            })

        start = max(start, prev_end + MIN_GAP)

        # Bounce curve for cartoon-style exaggeration
        t = (i % steps) / steps
        bounce_curve = (np.sin(np.pi * t) ** 2)  # [0..1] full curve
        jitter = random.uniform(0.01, 0.08) if random.random() < JITTER_PROB else 0

        weight = MIN_MORPH_WEIGHT + bounce_curve * (MAX_MORPH_WEIGHT - MIN_MORPH_WEIGHT) + jitter
        weight = min(MAX_MORPH_WEIGHT, round(weight, 2))

        # Boost explosive consonants for emphasis
        if char in ["P", "B", "M"]:
            weight = min(MAX_MORPH_WEIGHT, weight + 0.15)

        morph_targets.append({
            "morph": morph,
            "start": round(start, 3),
            "end": round(end, 3),
            "weight": weight,
            "fade_in": fade_duration,
            "fade_out": fade_duration
        })

        prev_end = end
        prev_morph = morph

    return morph_targets
