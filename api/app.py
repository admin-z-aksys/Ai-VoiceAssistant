import io, json, base64, re, traceback
import numpy as np
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydub import AudioSegment
from faster_whisper import WhisperModel
from dotenv import load_dotenv
import soundfile as sf
import os

from config import Config
from rag import retrieve_context
from tts import synthesize_with_phonemes
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory

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
print("📦 Loading faster-whisper (GPU)...")
whisper_model = WhisperModel("tiny.en", compute_type="float16", device="cuda")

print("🧠 Loading LLM model...")
llm = ChatGroq(model="llama3-70b-8192", api_key=os.getenv("GROQ_API_KEY"))
memory = ConversationBufferMemory(memory_key="history", return_messages=True)
prompt_template = PromptTemplate(
    input_variables=["history", "input", "context"],
    template="{history}\nUser: {input}\nContext: {context}\nAssistant:"
)

def convert_to_wav(audio_bytes: bytes) -> bytes:
    print("🔄 Converting audio to WAV...")
    audio = AudioSegment.from_file(io.BytesIO(audio_bytes))
    audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)
    buffer = io.BytesIO()
    audio.export(buffer, format="wav")
    return buffer.getvalue()

def clean_text(text: str) -> str:
    return re.sub(r"[^\x00-\x7F]+", "", text)

@app.post("/speak")
async def speak(request: Request):
    try:
        print("📥 Incoming /speak request")
        body = await request.body()
        base64_audio = json.loads(body).get("audio")
        if not base64_audio:
            raise HTTPException(status_code=400, detail="Missing audio")

        audio_bytes = base64.b64decode(base64_audio.split(",")[-1])
        wav_bytes = convert_to_wav(audio_bytes)

        data, sr = sf.read(io.BytesIO(wav_bytes))
        audio_np = np.array(data, dtype=np.float32)

        print("🔍 Transcribing with faster-whisper (GPU)...")
        segments, _ = whisper_model.transcribe(audio_np, beam_size=1, language="en")
        user_text = " ".join([s.text.strip() for s in segments]) or "Who is probation officer?"
        print("📝 Transcription:", user_text)

        context = retrieve_context(user_text) if len(user_text.split()) > 2 else ""
        full_prompt = prompt_template.format(history=memory.load_memory_variables({}).get("history", ""), input=user_text, context=context)

        print("💡 Generating response...")
        response = llm.invoke(full_prompt)
        assistant_text = getattr(response, "content", str(response)).strip()
        assistant_text = clean_text(assistant_text)
        memory.save_context({"input": user_text}, {"output": assistant_text})

        print("🔊 Synthesizing speech with GPU...")
        tts_result = synthesize_with_phonemes(assistant_text)
        if not tts_result:
            raise HTTPException(status_code=500, detail="TTS failed")

        base64_audio_response = base64.b64encode(tts_result["audio"]).decode("utf-8")

        return {
            "transcription": user_text,
            "response_text": assistant_text,
            "audio_base64": f"data:audio/wav;base64,{base64_audio_response}",
            "phonemes": tts_result["phonemes"],
            "morph_targets": tts_result["morph_targets"]
        }

    except Exception as e:
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": str(e)})
