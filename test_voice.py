"""
PRPCEM College Assistant - Voice STT & TTS Automated Test Suite
Validates Web Speech API integration, Speech-to-Text, Text-to-Speech,
DOM wiring, text cleaner for speech, privacy guarantees, and settings.
"""

import unittest
import os
import re
from app import app
from chatbot.chatbot_engine import chatbot_engine

class TestPRPCEMVoiceModule(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = app.test_client()
        with open(os.path.join("static", "js", "voice.js"), "r", encoding="utf-8") as f:
            cls.voice_js = f.read()
        with open(os.path.join("static", "js", "chatbot.js"), "r", encoding="utf-8") as f:
            cls.chatbot_js = f.read()
        with open(os.path.join("templates", "index.html"), "r", encoding="utf-8") as f:
            cls.index_html = f.read()

    def test_01_no_external_ai_voice_api(self):
        """Zero third-party voice APIs (No Google Cloud Speech, ElevenLabs, Whisper, Azure, AWS)."""
        forbidden_keywords = [
            "elevenlabs", "openai", "whisper", "google.cloud.speech",
            "azure.cognitiveservices", "aws.polly", "deepgram", "assemblyai"
        ]
        for kw in forbidden_keywords:
            self.assertNotIn(kw, self.voice_js.lower(), f"Forbidden external API found: {kw}")

    def test_02_web_speech_api_standards(self):
        """Ensures browser native Web Speech API standards are properly utilized."""
        self.assertIn("SpeechRecognition", self.voice_js)
        self.assertIn("webkitSpeechRecognition", self.voice_js)
        self.assertIn("window.speechSynthesis", self.voice_js)
        self.assertIn("SpeechSynthesisUtterance", self.voice_js)

    def test_03_stt_features(self):
        """Validates STT configuration: interim results, mic states, language, error handling."""
        self.assertIn("interimResults", self.voice_js)
        self.assertIn("setMicState", self.voice_js)
        self.assertIn("handleSpeechError", self.voice_js)
        self.assertIn("not-allowed", self.voice_js)
        self.assertIn("no-speech", self.voice_js)

    def test_04_tts_speech_cleaning(self):
        """Validates regex text cleaning for speech output."""
        def py_clean_text_for_speech(text):
            text = re.sub(r"https?://[^\s]+", "", text)
            text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
            text = re.sub(r"\*(.*?)\*", r"\1", text)
            text = re.sub(r"<[^>]+>", "", text)
            text = re.sub(r"^[•\-\*]\s+", "", text, flags=re.MULTILINE)
            text = re.sub(r"^\d+\.\s+", "", text, flags=re.MULTILINE)
            text = re.sub(r"source:.*$", "", text, flags=re.IGNORECASE | re.MULTILINE)
            text = re.sub(r"view source.*", "", text, flags=re.IGNORECASE)
            text = re.sub(r"\n{2,}", ". ", text)
            text = re.sub(r"\n", ". ", text)
            text = re.sub(r"\.\s*\.\s*\.", ".", text)
            return re.sub(r"\s+", " ", text).strip()

        sample_answer = (
            "According to official PRPCEM placement records:\n"
            "• **Tata Consultancy Services (TCS)**\n"
            "• **IBM**\n"
            "• **Cognizant**\n\n"
            "For inquiries visit https://prpotepatilengg.ac.in/placement.\n"
            "Source: PRPCEM Official Website"
        )
        cleaned = py_clean_text_for_speech(sample_answer)
        self.assertNotIn("https://", cleaned)
        self.assertNotIn("**", cleaned)
        self.assertNotIn("•", cleaned)
        self.assertNotIn("Source: PRPCEM", cleaned)
        self.assertIn("Tata Consultancy Services", cleaned)

    def test_05_voice_settings_supported_languages(self):
        """Validates that English (India), Hindi, and Marathi are supported."""
        self.assertIn("en-IN", self.voice_js)
        self.assertIn("hi-IN", self.voice_js)
        self.assertIn("mr-IN", self.voice_js)

    def test_06_dom_integration(self):
        """Validates that templates/index.html and chatbot.js properly bind voice controls."""
        # Index.html
        self.assertIn('id="micBtn"', self.index_html)
        self.assertIn('id="menuVoiceSettings"', self.index_html)
        self.assertIn('<script src="/static/js/voice.js"></script>', self.index_html)

        # Chatbot.js
        self.assertIn("window.VoiceModule.init()", self.chatbot_js)
        self.assertIn("window.VoiceModule.startListening()", self.chatbot_js)
        self.assertIn("window.VoiceModule.attachSpeakerBtn", self.chatbot_js)
        self.assertIn("window.VoiceModule.openVoiceSettings()", self.chatbot_js)

    def test_07_api_chat_answers_are_speech_compatible(self):
        """Validates that chat API answers can be cleanly converted to speech utterances."""
        test_queries = [
            "Who is the Principal?",
            "Who is the Dean?",
            "What is college timing?",
            "Which companies come for placement?",
            "Who is the HOD of Mechanical?"
        ]
        for q in test_queries:
            resp = self.client.post("/api/chat", json={"message": q, "session_id": "test_voice_api"})
            self.assertEqual(resp.status_code, 200)
            data = resp.get_json()
            self.assertTrue(len(data.get("answer", "")) > 10)
            self.assertIn(data.get("card_type"), ["verified_card", "text", "cutoff_card"])

if __name__ == "__main__":
    unittest.main()
