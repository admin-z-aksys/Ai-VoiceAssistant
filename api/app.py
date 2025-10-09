# import io, json, base64, re, traceback
# import numpy as np
# from fastapi import FastAPI, Request, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import JSONResponse
# from pydub import AudioSegment
# from faster_whisper import WhisperModel
# from dotenv import load_dotenv
# import soundfile as sf
# import os

# from config import Config
# from rag import retrieve_context
# from tts import synthesize_with_phonemes
# from langchain_groq import ChatGroq
# from langchain.prompts import PromptTemplate
# from langchain.memory import ConversationBufferMemory

# load_dotenv()

# app = FastAPI()
# origins = ["*"]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=False,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
# print("📦 Loading faster-whisper (GPU)...")
# whisper_model = WhisperModel("medium.en", compute_type="int8", device="cpu")

# print("🧠 Loading LLM model...")
# llm = ChatGroq(model="llama-3.1-8b-instant", api_key=os.getenv("GROQ_API_KEY"))
# memory = ConversationBufferMemory(memory_key="history", return_messages=True)
# prompt_template = PromptTemplate(
#     input_variables=["history", "input", "context"],
#     template="""
# {history}
# User: {input}
# Context: {context}

# Assistant:
# You must answer **only** using the information provided in the context.
# - If the context contains relevant information, use it to answer briefly and clearly.
# - If the context is empty or not related to the question, do **not** guess or bring outside knowledge.
# - In that case, respond instead with a short description of Berge Bulk:

# "Berge Bulk is one of the world’s leading dry bulk ship owners, operating a fleet of modern, fuel-efficient vessels."
# """
# )


# def convert_to_wav(audio_bytes: bytes) -> bytes:
#     print("🔄 Converting audio to WAV...")
#     audio = AudioSegment.from_file(io.BytesIO(audio_bytes))
#     audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)
#     buffer = io.BytesIO()
#     audio.export(buffer, format="wav")
#     return buffer.getvalue()

# def clean_text(text: str) -> str:
#     return re.sub(r"[^\x00-\x7F]+", "", text)

# @app.get("/health")
# def home():
#     return {"message":"API is running"}

# @app.post("/speak")
# async def speak(request: Request):
#     try:
#         print("📥 Incoming /speak request")
#         body = await request.body()
#         base64_audio = json.loads(body).get("audio")
#         if not base64_audio:
#             raise HTTPException(status_code=400, detail="Missing audio")

#         audio_bytes = base64.b64decode(base64_audio.split(",")[-1])
#         wav_bytes = convert_to_wav(audio_bytes)

#         data, sr = sf.read(io.BytesIO(wav_bytes))
#         audio_np = np.array(data, dtype=np.float32)

#         print("🔍 Transcribing with faster-whisper (GPU)...")
#         segments, _ = whisper_model.transcribe(audio_np, beam_size=1, language="en")
#         user_text = " ".join([s.text.strip() for s in segments]) or "who is Virat Kohli?"
#         print("📝 Transcription:", user_text)

#         context = retrieve_context(user_text) if len(user_text.split()) > 2 else ""
#         full_prompt = prompt_template.format(history=memory.load_memory_variables({}).get("history", ""), input=user_text, context=context)

#         print("💡 Generating response...")
#         response = llm.invoke(full_prompt)
#         assistant_text = getattr(response, "content", str(response)).strip()
#         assistant_text = clean_text(assistant_text)
#         memory.save_context({"input": user_text}, {"output": assistant_text})

#         print("🔊 Synthesizing speech with GPU...")
#         tts_result = synthesize_with_phonemes(assistant_text)
#         if not tts_result:
#             raise HTTPException(status_code=500, detail="TTS failed")

#         base64_audio_response = base64.b64encode(tts_result["audio"]).decode("utf-8")

#         return {
#             "transcription": user_text,
#             "response_text": assistant_text,
#             "audio_base64": f"data:audio/wav;base64,{base64_audio_response}",
#             "phonemes": tts_result["phonemes"],
#             "morph_targets": tts_result["morph_targets"]
#         }

#     except Exception as e:
#         traceback.print_exc()
#         return JSONResponse(status_code=500, content={"error": str(e)})


# import io
# import json
# import base64
# import re
# import traceback
# import os
# from typing import List

# import numpy as np
# import soundfile as sf
# from fastapi import FastAPI, Request, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import JSONResponse
# from pydub import AudioSegment
# from faster_whisper import WhisperModel
# from dotenv import load_dotenv

# from config import Config
# from rag import retrieve_context
# from tts import synthesize_with_phonemes
# from langchain_groq import ChatGroq
# from langchain.prompts import PromptTemplate
# from langchain.memory import ConversationBufferMemory


# # ===========================
# # Environment & App
# # ===========================
# load_dotenv()

# app = FastAPI()
# origins = ["*"]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=False,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )


# # ===========================
# # Models (CPU by default)
# # ===========================
# print("📦 Loading faster-whisper (CPU)...")
# # If you have a CUDA GPU, set device="cuda" and consider compute_type="float16".
# whisper_model = WhisperModel("medium.en", compute_type="int8", device="cpu")

# print("🧠 Loading LLM model...")
# llm = ChatGroq(model="llama-3.1-8b-instant", api_key=os.getenv("GROQ_API_KEY"))
# memory = ConversationBufferMemory(memory_key="history", return_messages=True)

# prompt_template = PromptTemplate(
#     input_variables=["history", "input", "context"],
#     template=(
#         "{history}\n"
#         "User: {input}\n"
#         "Context: {context}\n\n"
#         "Assistant:\n"
#         "You must answer **only** using the information provided in the context.\n"
#         "- If the context contains relevant information, use it to answer briefly and clearly.\n"
#         "- If the context is empty or not related to the question, do **not** guess or bring outside knowledge.\n"
#         "- In that case, respond instead with a short description of Berge Bulk:\n\n"
#         "\"Berge Bulk is one of the world’s leading dry bulk ship owners, operating a fleet of modern, fuel-efficient vessels.\""
#     )
# )


# # ===========================
# # Audio helpers
# # ===========================
# def convert_to_wav(audio_bytes: bytes) -> bytes:
#     """
#     Convert arbitrary input audio bytes to 16 kHz / mono / 16-bit WAV.
#     Requires ffmpeg to be installed for pydub.
#     """
#     print("🔄 Converting audio to WAV...")
#     audio = AudioSegment.from_file(io.BytesIO(audio_bytes))
#     audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)
#     buffer = io.BytesIO()
#     audio.export(buffer, format="wav")
#     return buffer.getvalue()


# def clean_text(text: str) -> str:
#     """
#     Strip non-ASCII (optional). If you need Unicode, replace this with NFKC normalization.
#     """
#     return re.sub(r"[^\x00-\x7F]+", "", text)


# # ===========================
# # BRAND-NAME FIXES (ONLY)
# # ===========================
# _CANON_BRAND = "Berge Bulk"

# # Curated common mis-hearings; add more as you observe them in logs.
# _BAD_BRAND_PATTERNS: List[str] = [
#     r"burji\s*buk", r"burji\s*buk[ck]", r"burjibuk",
#     r"berge\s*bul[ck]", r"bergebulk", r"burgebulk",
#     r"burge\s*bulk", r"burgi\s*bulk", r"berg\s*bukl",
#     r"berg\s*bulk", r"berji\s*bulk", r"birji\s*bulk",
#     r"burji\s*bulk", r"bergy\s*bulk", r"bargi\s*bulk",
# ]
# _BAD_BRAND_RE = re.compile(r"\b(?:" + r"|".join(_BAD_BRAND_PATTERNS) + r")\b", re.IGNORECASE)


# def build_stt_bias_prompt() -> str:
#     """
#     Initial prompt to bias Whisper towards your domain vocabulary.
#     Keep it short; repeat tricky terms a couple of times.
#     """
#     return (
#         "Vocabulary: Berge Bulk, BergeBulk.\n"
#         "Brand name appears often: Berge Bulk. Berge Bulk. Berge Bulk."
#     )


# def normalize_brand(text: str) -> str:
#     """
#     Normalize common mis-hearings of the brand to the canonical spelling.
#     Also fixes joined forms like 'bergebulk' → 'Berge Bulk'.
#     """
#     t = re.sub(r"\s+", " ", text).strip()
#     t = _BAD_BRAND_RE.sub(_CANON_BRAND, t)
#     # Handle joined/near-joined variants + optional space (e.g., bergebulk / ber ge bulk)
#     t = re.sub(r"\bber?ge?\s*bulk\b", _CANON_BRAND, t, flags=re.IGNORECASE)
#     return t


# def fix_tts_brand_pronunciation(text: str) -> str:
#     """
#     Optional: if TTS ever mispronounces the brand, nudge with a phonetic hint.
#     This only affects audio; the visible text returned to the client stays unchanged.
#     Adjust the phonetics if your preferred sound differs.
#     """
#     return re.sub(r"\bBerge Bulk\b", "Bur-juh Bulk", text)


# # ===========================
# # Routes
# # ===========================
# @app.get("/health")
# def home():
#     return {"message": "API is running"}


# @app.post("/speak")
# async def speak(request: Request):
#     try:
#         print("📥 Incoming /speak request")
#         body = await request.body()
#         base64_audio = json.loads(body).get("audio")
#         if not base64_audio:
#             raise HTTPException(status_code=400, detail="Missing audio")

#         # Decode and convert to WAV (16k mono)
#         audio_bytes = base64.b64decode(base64_audio.split(",")[-1])
#         wav_bytes = convert_to_wav(audio_bytes)

#         # Load audio for Whisper
#         data, sr = sf.read(io.BytesIO(wav_bytes))
#         audio_np = np.array(data, dtype=np.float32)

#         # STT with bias prompt and stable decoding params
#         print("🔍 Transcribing with faster-whisper (CPU)...")
#         bias_prompt = build_stt_bias_prompt()
#         segments, _ = whisper_model.transcribe(
#             audio_np,
#             language="en",
#             beam_size=3,        # balance of accuracy/latency
#             best_of=5,
#             temperature=0.0,    # deterministic
#             vad_filter=True,    # trims silence
#             initial_prompt=bias_prompt
#         )

#         # Concatenate segments and normalize BRAND ONLY
#         user_text = " ".join([s.text.strip() for s in segments]) or "what is Berge Bulk?"
#         user_text = normalize_brand(user_text)
#         print("📝 Transcription (normalized):", user_text)

#         # RAG context
#         context = retrieve_context(user_text) if len(user_text.split()) > 2 else ""

#         # Prompt LLM
#         full_prompt = prompt_template.format(
#             history=memory.load_memory_variables({}).get("history", ""),
#             input=user_text,
#             context=context
#         )

#         print("💡 Generating response...")
#         response = llm.invoke(full_prompt)
#         assistant_text = getattr(response, "content", str(response)).strip()
#         assistant_text = clean_text(assistant_text)
#         memory.save_context({"input": user_text}, {"output": assistant_text})

#         # TTS (optionally tweak brand pronunciation for audio only)
#         print("🔊 Synthesizing speech...")
#         assistant_text_tts = fix_tts_brand_pronunciation(assistant_text)
#         tts_result = synthesize_with_phonemes(assistant_text_tts)
#         if not tts_result:
#             raise HTTPException(status_code=500, detail="TTS failed")

#         base64_audio_response = base64.b64encode(tts_result["audio"]).decode("utf-8")

#         return {
#             "transcription": user_text,
#             "response_text": assistant_text,
#             "audio_base64": f"data:audio/wav;base64,{base64_audio_response}",
#             "phonemes": tts_result["phonemes"],
#             "morph_targets": tts_result["morph_targets"],
#         }

#     except Exception as e:
#         traceback.print_exc()
#         return JSONResponse(status_code=500, content={"error": str(e)})





# import io, json, base64, re, traceback
# import numpy as np
# from fastapi import FastAPI, Request, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import JSONResponse
# from pydub import AudioSegment
# from faster_whisper import WhisperModel
# from dotenv import load_dotenv
# import soundfile as sf
# import os

# from config import Config
# from rag import retrieve_context
# from tts import synthesize_with_phonemes
# from langchain_groq import ChatGroq
# from langchain.prompts import PromptTemplate
# from langchain.memory import ConversationBufferMemory

# load_dotenv()

# app = FastAPI()
# origins = ["*"]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=False,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
# print("📦 Loading faster-whisper (GPU)...")
# whisper_model = WhisperModel("medium.en", compute_type="int8", device="cpu")

# print("🧠 Loading LLM model...")
# llm = ChatGroq(model="llama-3.1-8b-instant", api_key=os.getenv("GROQ_API_KEY"))
# memory = ConversationBufferMemory(memory_key="history", return_messages=True)
# prompt_template = PromptTemplate(
#     input_variables=["history", "input", "context"],
#     template="""
# {history}
# User: {input}
# Context: {context}

# Assistant:
# You must answer **only** using the information provided in the context.
# - If the context contains relevant information, use it to answer briefly and clearly.
# - If the context is empty or not related to the question, do **not** guess or bring outside knowledge.
# - In that case, respond instead with a short description of Berge Bulk:

# "Berge Bulk is one of the world’s leading dry bulk ship owners, operating a fleet of modern, fuel-efficient vessels."
# """
# )


# def convert_to_wav(audio_bytes: bytes) -> bytes:
#     print("🔄 Converting audio to WAV...")
#     audio = AudioSegment.from_file(io.BytesIO(audio_bytes))
#     audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)
#     buffer = io.BytesIO()
#     audio.export(buffer, format="wav")
#     return buffer.getvalue()

# def clean_text(text: str) -> str:
#     return re.sub(r"[^\x00-\x7F]+", "", text)

# @app.get("/health")
# def home():
#     return {"message":"API is running"}

# @app.post("/speak")
# async def speak(request: Request):
#     try:
#         print("📥 Incoming /speak request")
#         body = await request.body()
#         base64_audio = json.loads(body).get("audio")
#         if not base64_audio:
#             raise HTTPException(status_code=400, detail="Missing audio")

#         audio_bytes = base64.b64decode(base64_audio.split(",")[-1])
#         wav_bytes = convert_to_wav(audio_bytes)

#         data, sr = sf.read(io.BytesIO(wav_bytes))
#         audio_np = np.array(data, dtype=np.float32)

#         print("🔍 Transcribing with faster-whisper (GPU)...")
#         segments, _ = whisper_model.transcribe(audio_np, beam_size=1, language="en")
#         user_text = " ".join([s.text.strip() for s in segments]) or "who is Virat Kohli?"
#         print("📝 Transcription:", user_text)

#         context = retrieve_context(user_text) if len(user_text.split()) > 2 else ""
#         full_prompt = prompt_template.format(history=memory.load_memory_variables({}).get("history", ""), input=user_text, context=context)

#         print("💡 Generating response...")
#         response = llm.invoke(full_prompt)
#         assistant_text = getattr(response, "content", str(response)).strip()
#         assistant_text = clean_text(assistant_text)
#         memory.save_context({"input": user_text}, {"output": assistant_text})

#         print("🔊 Synthesizing speech with GPU...")
#         tts_result = synthesize_with_phonemes(assistant_text)
#         if not tts_result:
#             raise HTTPException(status_code=500, detail="TTS failed")

#         base64_audio_response = base64.b64encode(tts_result["audio"]).decode("utf-8")

#         return {
#             "transcription": user_text,
#             "response_text": assistant_text,
#             "audio_base64": f"data:audio/wav;base64,{base64_audio_response}",
#             "phonemes": tts_result["phonemes"],
#             "morph_targets": tts_result["morph_targets"]
#         }

#     except Exception as e:
#         traceback.print_exc()
#         return JSONResponse(status_code=500, content={"error": str(e)})


import io
import json
import base64
import re
import traceback
import os
from typing import List

import numpy as np
import soundfile as sf
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydub import AudioSegment
from faster_whisper import WhisperModel
from dotenv import load_dotenv

from config import Config
from rag import retrieve_context
from tts import synthesize_with_phonemes
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory


# ===========================
# Environment & App
# ===========================
load_dotenv()

app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===========================
# Models (CPU by default)
# ===========================
print("📦 Loading faster-whisper (CPU)...")
# If you have a CUDA GPU, set device="cuda" and consider compute_type="float16".
whisper_model = WhisperModel("medium.en", compute_type="int8", device="cpu")

print("🧠 Loading LLM model...")
llm = ChatGroq(model="llama-3.1-8b-instant", api_key=os.getenv("GROQ_API_KEY"))
memory = ConversationBufferMemory(memory_key="history", return_messages=True)

prompt_template = PromptTemplate(
    input_variables=["history", "input", "context"],
    template=(
        "{history}\n"
        "User: {input}\n"
        "Context: {context}\n\n"
        "Assistant:\n"
        "You must answer **only** using the information provided in the context.\n"
        "- If the context contains relevant information, use it to answer briefly and clearly.\n"
        "- If the context is empty or not related to the question, do **not** guess or bring outside knowledge.\n"
        "- In that case, respond instead with a short description of Berge Bulk:\n\n"
        "\"Berge Bulk is one of the world’s leading dry bulk ship owners, operating a fleet of modern, fuel-efficient vessels.\""
    )
)


# ===========================
# Audio helpers
# ===========================
def convert_to_wav(audio_bytes: bytes) -> bytes:
    """
    Convert arbitrary input audio bytes to 16 kHz / mono / 16-bit WAV.
    Requires ffmpeg to be installed for pydub.
    """
    print("🔄 Converting audio to WAV...")
    audio = AudioSegment.from_file(io.BytesIO(audio_bytes))
    audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)
    buffer = io.BytesIO()
    audio.export(buffer, format="wav")
    return buffer.getvalue()


def clean_text(text: str) -> str:
    """
    Strip non-ASCII (optional). If you need Unicode, replace this with NFKC normalization.
    """
    return re.sub(r"[^\x00-\x7F]+", "", text)


# ===========================
# BRAND-NAME FIXES (ONLY)
# ===========================
_CANON_BRAND = "Berge Bulk"

# Curated common mis-hearings; add more as you observe them in logs.
_BAD_BRAND_PATTERNS: List[str] = [
    r"burji\s*buk", r"burji\s*buk[ck]", r"burjibuk",
    r"berge\s*bul[ck]", r"bergebulk", r"burgebulk",
    r"burge\s*bulk", r"burgi\s*bulk", r"berg\s*bukl",
    r"berg\s*bulk", r"berji\s*bulk", r"birji\s*bulk",
    r"burji\s*bulk", r"bergy\s*bulk", r"bargi\s*bulk",
]
_BAD_BRAND_RE = re.compile(r"\b(?:" + r"|".join(_BAD_BRAND_PATTERNS) + r")\b", re.IGNORECASE)


def build_stt_bias_prompt() -> str:
    """
    Initial prompt to bias Whisper towards your domain vocabulary.
    Keep it short; repeat tricky terms a couple of times.
    """
    return (
        "Vocabulary: Berge Bulk, BergeBulk.\n"
        "Brand name appears often: Berge Bulk. Berge Bulk. Berge Bulk."
    )


def normalize_brand(text: str) -> str:
    """
    Normalize common mis-hearings of the brand to the canonical spelling.
    Also fixes joined forms like 'bergebulk' → 'Berge Bulk'.
    """
    t = re.sub(r"\s+", " ", text).strip()
    t = _BAD_BRAND_RE.sub(_CANON_BRAND, t)
    # Handle joined/near-joined variants + optional space (e.g., bergebulk / ber ge bulk)
    t = re.sub(r"\bber?ge?\s*bulk\b", _CANON_BRAND, t, flags=re.IGNORECASE)
    return t


def fix_tts_brand_pronunciation(text: str) -> str:
    """
    Optional: if TTS ever mispronounces the brand, nudge with a phonetic hint.
    This only affects audio; the visible text returned to the client stays unchanged.
    Adjust the phonetics if your preferred sound differs.
    """
    return re.sub(r"\bBerge Bulk\b", "Bur-juh Bulk", text)


# ===========================
# Routes
# ===========================
@app.get("/health")
def home():
    return {"message": "API is running"}


@app.post("/speak")
async def speak(request: Request):
    try:
        print("📥 Incoming /speak request")
        body = await request.body()
        base64_audio = json.loads(body).get("audio")
        if not base64_audio:
            raise HTTPException(status_code=400, detail="Missing audio")

        # Decode and convert to WAV (16k mono)
        audio_bytes = base64.b64decode(base64_audio.split(",")[-1])
        wav_bytes = convert_to_wav(audio_bytes)

        # Load audio for Whisper
        data, sr = sf.read(io.BytesIO(wav_bytes))
        audio_np = np.array(data, dtype=np.float32)

        # STT with bias prompt and stable decoding params
        print("🔍 Transcribing with faster-whisper (CPU)...")
        bias_prompt = build_stt_bias_prompt()
        segments, _ = whisper_model.transcribe(
            audio_np,
            language="en",
            beam_size=3,        # balance of accuracy/latency
            best_of=5,
            temperature=0.0,    # deterministic
            vad_filter=True,    # trims silence
            initial_prompt=bias_prompt
        )

        # Concatenate segments and normalize BRAND ONLY
        user_text = " ".join([s.text.strip() for s in segments]) or "what is Berge Bulk?"
        user_text = normalize_brand(user_text)
        print("📝 Transcription (normalized):", user_text)

        # RAG context
        context = retrieve_context(user_text) if len(user_text.split()) > 2 else ""

        # Prompt LLM
        full_prompt = prompt_template.format(
            history=memory.load_memory_variables({}).get("history", ""),
            input=user_text,
            context=context
        )

        print("💡 Generating response...")
        response = llm.invoke(full_prompt)
        assistant_text = getattr(response, "content", str(response)).strip()
        assistant_text = clean_text(assistant_text)
        memory.save_context({"input": user_text}, {"output": assistant_text})

        # TTS (optionally tweak brand pronunciation for audio only)
        print("🔊 Synthesizing speech...")
        assistant_text_tts = fix_tts_brand_pronunciation(assistant_text)
        tts_result = synthesize_with_phonemes(assistant_text_tts)
        if not tts_result:
            raise HTTPException(status_code=500, detail="TTS failed")

        base64_audio_response = base64.b64encode(tts_result["audio"]).decode("utf-8")

        return {
            "transcription": user_text,
            "response_text": assistant_text,
            "audio_base64": f"data:audio/wav;base64,{base64_audio_response}",
            "phonemes": tts_result["phonemes"],
            "morph_targets": tts_result["morph_targets"],
        }

    except Exception as e:
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": str(e)})

