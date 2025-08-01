import unittest
from tts import synthesize_with_phonemes

class TestTTSWithPhonemes(unittest.TestCase):

    def test_valid_synthesis(self):
        text = "Hello, how are you?"
        result = synthesize_with_phonemes(text)

        # Basic output structure validation
        self.assertIsNotNone(result, "Result should not be None")
        self.assertIn("audio", result)
        self.assertIn("phonemes", result)
        self.assertIn("morph_targets", result)

        # Validate audio
        self.assertIsInstance(result["audio"], (bytes, bytearray), "Audio should be bytes")
        self.assertGreater(len(result["audio"]), 1000, "Audio data is too small")

        # Validate phoneme timeline
        phonemes = result["phonemes"]
        self.assertIsInstance(phonemes, list)
        self.assertGreater(len(phonemes), 0, "Phoneme timeline should not be empty")
        for p in phonemes:
            self.assertIn("char", p)
            self.assertIn("start", p)
            self.assertIn("end", p)

        # Validate morph targets
        morphs = result["morph_targets"]
        self.assertIsInstance(morphs, list)
        self.assertGreater(len(morphs), 0, "Morph targets should be generated")
        for m in morphs:
            self.assertIn("morph", m)
            self.assertIn("start", m)
            self.assertIn("end", m)
            self.assertIn("weight", m)

    def test_empty_input(self):
        result = synthesize_with_phonemes("")
        self.assertIsNone(result, "Empty input should return None")

    def test_short_input(self):
        result = synthesize_with_phonemes("Hi")
        self.assertIsNotNone(result, "Should still synthesize short input")
        self.assertGreaterEqual(len(result["morph_targets"]), 1, "Should include at least one morph")

if __name__ == "__main__":
    unittest.main()
