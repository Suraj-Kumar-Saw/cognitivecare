"""
Gemini AI service — Python port of src/services/geminiService.ts
Uses the new google-genai SDK.
"""
import json
import base64
from datetime import datetime
from django.conf import settings
from google import genai
from google.genai import types
import logging

logger = logging.getLogger(__name__)

def _client():
    return genai.Client(api_key=settings.GEMINI_API_KEY)

SYSTEM_PROMPT = """You are "Memory Companion", a virtual assistant for a patient with early-to-middle stage Alzheimer's.
Your goal is to provide factually grounded, reassuring, and simple answers based ONLY on the provided Knowledge Base and Schedule.

Strict Instructions:
1. Answer ONLY using the Knowledge Base, Schedule, Habits, Tasks, and Current Date/Time context. Do not use outside knowledge.
2. If the user asks if they completed a routine, task, or habit:
   - If the Status is 'Completed' or they met their habit target, confirm it warmly.
   - If the Status is 'Pending' or they haven't met their target, state that it hasn't been completed yet, and suggest they confirm with their caregiver if they are unsure.
3. Handling Uncertainty (CRITICAL):
   - High Confidence (0.9 - 1.0): The answer is clearly in the context. Provide a direct, warm answer.
   - Medium Confidence (0.7 - 0.89): Provide the answer but suggest double-checking with their caregiver.
   - Low Confidence (< 0.7): DO NOT guess or hallucinate. Redirect warmly to the caregiver.
4. Use a warm, calm, and supportive tone. Use the patient's name (Arthur) if appropriate.
5. Keep responses to 1-3 short, simple sentences.
6. Provide a confidence score (0.0 to 1.0).
7. If the user expresses self-harm, suicide ideation, or severe distress, set crisis_detected to true, risk_level to 'high', and include emergency hotline info in the answer.
8. AUDIO ANALYSIS: If an audio file is provided, analyze the acoustic features to determine emotion, mental health state, and energy level.
9. NEVER provide medical diagnoses. NEVER replace licensed therapy. NEVER encourage harmful behavior.

You MUST respond with ONLY valid JSON:
{
  "answer": "string",
  "confidence": 0.0,
  "factId": null,
  "reasoning": "string",
  "emotion": "string",
  "sentiment_score": 0.0,
  "risk_level": "low",
  "energy_level": "string",
  "crisis_detected": false,
  "therapy_suggestion": ""
}"""


def query_memory(
    query: str,
    facts: list,
    history: list = None,
    routines: list = None,
    current_time: datetime = None,
    completed_routine_ids: list = None,
    habits: list = None,
    tasks: list = None,
    emotional_logs: list = None,
    audio_data: dict = None,
) -> dict:
    logger.info(f"Preparing memory query context for prompt. Query: {query}")
    history = history or []
    routines = routines or []
    completed_routine_ids = completed_routine_ids or []
    habits = habits or []
    tasks = tasks or []
    emotional_logs = emotional_logs or []
    current_time = current_time or datetime.now()

    context = "\n".join(
        f"ID: {f['id']} | Category: {f['category']} | Fact: {f['fact']} | Details: {f['details']}"
        for f in facts
    )
    routines_ctx = "\n".join(
        f"ID: {r['id']} | Time: {r['time']} | Title: {r['title']} | Category: {r['category']} | "
        f"Status: {'Completed' if r['id'] in completed_routine_ids else 'Pending'}"
        for r in routines
    )
    habits_ctx = "\n".join(
        f"Habit: {h['title']} | Type: {'Build' if h['type'] == 'build' else 'Break'} | "
        f"Target: {h['target_count']}/day | Today: {h['current_count']}"
        for h in habits
    )
    tasks_ctx = "\n".join(
        f"Task: {t['title']} | Due: {t['due_date']} | Status: {'Completed' if t['completed'] else 'Pending'}"
        for t in tasks
    )
    emotional_ctx = "\n".join(
        f"Time: {l['timestamp']} | Emotion: {l['emotion']} | Sentiment: {l['sentiment_score']}"
        for l in emotional_logs[-5:]
    )
    history_ctx = "\n".join(
        f"{'Patient' if m['role'] == 'user' else 'Assistant'}: {m['text']}"
        for m in history[-6:]
    )
    date_str = current_time.strftime('%A, %B %-d, %Y')
    time_str = current_time.strftime('%-I:%M %p')

    prompt = f"""Current Date and Time: Today is {date_str}. The current time is {time_str}.

Knowledge Base:
{context}

Daily Schedule/Routines:
{routines_ctx}

Habits:
{habits_ctx}

Tasks:
{tasks_ctx}

Recent Emotional State:
{emotional_ctx}

Recent Dialogue:
{history_ctx}

Patient Query: {query}"""

    logger.debug(f"Full query prompt generated:\n{prompt}")

    try:
        client = _client()
        parts = [types.Part.from_text(text=prompt)]

        if audio_data:
            try:
                raw = base64.b64decode(audio_data["base64"])
                parts.append(types.Part.from_bytes(data=raw, mime_type=audio_data["mimeType"]))
                logger.info(f"Audio data decoded and appended to parts. Mime Type: {audio_data.get('mimeType')}")
            except Exception as e:
                logger.error(f"Failed to decode audio data base64: {e}", exc_info=True)

        logger.info("Calling Gemini API generate_content")
        response = client.models.generate_content(
            model="gemini-3.0-flash",
            contents=types.Content(role="user", parts=parts),
            config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT),
        )
        raw_text = response.text.strip()
        logger.debug(f"Raw Gemini API response: {raw_text}")

        if raw_text.startswith("```"):
            lines = raw_text.split("\n")
            raw_text = "\n".join(lines[1:-1])

        try:
            result = json.loads(raw_text)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from Gemini API response: {e}. Raw text: {raw_text}", exc_info=True)
            raise e

        image_url = None
        if result.get("factId"):
            fact = next((f for f in facts if f["id"] == result["factId"]), None)
            if fact:
                image_url = fact.get("image_url")
        result["imageUrl"] = image_url
        logger.info("Successfully completed query_memory")
        return result
    except Exception as e:
        logger.error(f"Error executing query_memory: {e}", exc_info=True)
        raise e


def generate_speech(text: str) -> str | None:
    logger.info(f"Generating TTS for text length: {len(text) if text else 0}")
    if not text or not text.strip():
        logger.warning("Empty text for TTS generation")
        return None
    try:
        client = _client()
        logger.debug(f"Calling Gemini API generate_content for TTS")
        response = client.models.generate_content(
            model="gemini-2.5-flash-preview-tts",
            contents=f"Say: {text.strip()}",
            config=types.GenerateContentConfig(
                response_modalities=["AUDIO"],
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Kore")
                    )
                ),
            ),
        )
        part = response.candidates[0].content.parts[0]
        inline = getattr(part, "inline_data", None)
        if inline and inline.data:
            b64_audio = base64.b64encode(inline.data).decode("utf-8")
            logger.info("Successfully generated and encoded TTS audio")
            return b64_audio
        else:
            logger.warning("No audio inline_data returned in TTS response")
    except Exception as e:
        logger.error(f"TTS error: {e}", exc_info=True)
    return None


def get_helpful_tip() -> str:
    logger.info("Requesting helpful tip from Gemini")
    try:
        client = _client()
        response = client.models.generate_content(
            model="gemini-3.0-flash",
            contents="Provide a short, encouraging, and practical tip for someone with early-to-middle stage "
                     "Alzheimer's to help them manage their day. Keep it to 1-2 sentences. Warm and supportive tone.",
        )
        tip = response.text.strip()
        logger.info(f"Successfully received tip: {tip}")
        return tip
    except Exception as e:
        logger.error(f"Tip generation error: {e}", exc_info=True)
        return "Focus on one small task at a time. You're doing great."
