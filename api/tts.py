import io
import soundfile as sf
from TTS.api import TTS
from typing import Optional, Dict, Any, List
from g2p_en import G2p

from utils import generate_morph_targets_from_phonemes

# Constants
SAMPLE_RATE = 22050
FADE_DURATION = 0.04

# Load TTS model (GPU)
model_name = "tts_models/en/vctk/vits"
tts_model = TTS(model_name, progress_bar=False, gpu=True)
has_alignment = hasattr(tts_model, "tts_with_alignment")

g2p = G2p()

def build_phoneme_timeline(phonemes: List[str], durations: List[float]) -> List[Dict[str, Any]]:
    timeline = []
    current_time = 0.0

    for i, char in enumerate(phonemes):
        start = round(current_time, 3)
        end = round(current_time + durations[i], 3)
        timeline.append({
            "char": char,
            "start": start,
            "end": end
        })
        current_time = end

    return timeline

def synthesize_with_phonemes(text: str) -> Optional[Dict[str, Any]]:
    try:
        print("🎙️ [TTS] Synthesizing:", text)

        phonemes, durations = [], []

        if has_alignment:
            print("🔄 Using model alignment...")
            output = tts_model.tts_with_alignment(text, return_dict=True)
            waveform = output["wav"]
            phonemes = output.get("phoneme", [])
            durations_raw = output.get("phoneme_duration", [])

            total_d = sum(durations_raw)
            audio_duration = len(waveform) / SAMPLE_RATE
            durations = [(d / total_d) * audio_duration for d in durations_raw]

        else:
            print("⚠️ No alignment available, using g2p fallback.")
            waveform = tts_model.tts(text, speaker="p226")
            phonemes = [p for p in g2p(text) if p.isalpha()]
            audio_duration = len(waveform) / SAMPLE_RATE

            duration = audio_duration / max(len(phonemes), 1)
            durations = [duration] * len(phonemes)

        # Convert audio to base64-ready bytes
        buffer = io.BytesIO()
        sf.write(buffer, waveform, SAMPLE_RATE, format='WAV')
        audio_bytes = buffer.getvalue()

        # Timeline and morph targets
        timeline = build_phoneme_timeline(phonemes, durations)
        morph_targets = generate_morph_targets_from_phonemes(timeline)

        # Idle fill if too short
        if audio_duration > 0.5 and len(morph_targets) < 4:
            morph_targets.append({
                "morph": "Key 1",
                "start": round(morph_targets[-1]["end"], 3) if morph_targets else 0,
                "end": round(audio_duration, 3),
                "weight": 0.2,
                "fade_in": 0.05,
                "fade_out": 0.05
            })

        print(f"✅ Duration: {round(audio_duration, 3)}s")
        print(f"🔤 Phonemes: {len(phonemes)}")
        print(f"🎭 Morph targets: {len(morph_targets)}")

        return {
            "audio": audio_bytes,
            "phonemes": timeline,
            "morph_targets": morph_targets
        }

    except Exception as e:
        print(f"❌ [TTS ERROR]: {e}")
        return None
