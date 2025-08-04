import numpy as np
import random

# Parameters
MAX_MORPH_WEIGHT = 0.80
MIN_MORPH_WEIGHT = 0.03
MIN_GAP = 0.03
JITTER_PROB = 0.2
IDLE_FILLER_WEIGHT = 0.2

def generate_morph_targets_from_phonemes(phonemes, steps=100):
    morph_targets = []
    prev_end = 0.0

    for i, p in enumerate(phonemes):
        char = p.get("char", "").upper()
        start = round(p.get("start", 0), 3)
        end = round(p.get("end", 0), 3)
        duration = end - start

        if duration <= 0:
            continue

        morph = "Key 1"  # Fixed morph for cartoon mouth

        # Insert subtle idle morph if gap is too large
        gap = start - prev_end
        if gap > 0.3:
            morph_targets.append({
                "morph": "Key 1",
                "start": round(prev_end, 3),
                "end": round(start - MIN_GAP, 3),
                "weight": IDLE_FILLER_WEIGHT,
                "fade_in": 0.03,
                "fade_out": 0.03
            })

        start = max(start, prev_end + MIN_GAP)

        # Stylized bounce curve
        t = (i % steps) / steps
        bounce = np.sin(np.pi * t) ** 2  # smoother curve
        jitter = random.uniform(0.01, 0.05) if random.random() < JITTER_PROB else 0

        weight = MIN_MORPH_WEIGHT + bounce * (MAX_MORPH_WEIGHT - MIN_MORPH_WEIGHT) + jitter
        weight = round(min(MAX_MORPH_WEIGHT, weight), 3)

        morph_targets.append({
            "morph": morph,
            "start": round(start, 3),
            "end": round(end, 3),
            "weight": weight,
            "fade_in": 0.04,
            "fade_out": 0.04
        })

        prev_end = end

    return morph_targets
