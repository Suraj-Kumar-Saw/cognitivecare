import json
from datetime import date, datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.shortcuts import render
import logging

logger = logging.getLogger(__name__)
from .models import Routine, MemoryFact, LogEntry, Habit, Task, EmotionalLog, CrisisEvent
from .services import gemini


# ─── Page Views ───────────────────────────────────────────────────────────────

def index(request):
    logger.info(f"Executing index")
    logger.debug(f"Request method: {request.method}")
    logger.debug(f'Entering index {getattr(request, "method", "") if "request" in locals() else ""}')
    return render(request, 'care/index.html')


# ─── Helpers ──────────────────────────────────────────────────────────────────

def routine_to_dict(r):
    logger.info(f"Executing routine_to_dict")
    logger.debug(f'Entering routine_to_dict {getattr(request, "method", "") if "request" in locals() else ""}')
    return {
        'id': r.id, 'title': r.title, 'time': r.time,
        'category': r.category, 'alert_tier': r.alert_tier,
        'recurrence': r.recurrence, 'last_triggered': r.last_triggered,
    }

def fact_to_dict(f):
    logger.info(f"Executing fact_to_dict")
    logger.debug(f'Entering fact_to_dict {getattr(request, "method", "") if "request" in locals() else ""}')
    return {
        'id': f.id, 'category': f.category, 'fact': f.fact,
        'details': f.details, 'image_url': f.image_url,
        'timestamp': f.timestamp.isoformat(),
    }

def log_to_dict(l):
    logger.info(f"Executing log_to_dict")
    logger.debug(f'Entering log_to_dict {getattr(request, "method", "") if "request" in locals() else ""}')
    return {
        'id': l.id, 'timestamp': l.timestamp.isoformat(),
        'event_type': l.event_type, 'details': l.details,
        'alert_tier': l.alert_tier,
    }

def habit_to_dict(h):
    logger.info(f"Executing habit_to_dict")
    logger.debug(f'Entering habit_to_dict {getattr(request, "method", "") if "request" in locals() else ""}')
    return {
        'id': h.id, 'title': h.title, 'type': h.type,
        'target_count': h.target_count, 'current_count': h.current_count,
        'category': h.category, 'last_reset_date': h.last_reset_date,
    }

def task_to_dict(t):
    logger.info(f"Executing task_to_dict")
    logger.debug(f'Entering task_to_dict {getattr(request, "method", "") if "request" in locals() else ""}')
    return {
        'id': t.id, 'title': t.title, 'due_date': t.due_date,
        'completed': t.completed, 'category': t.category,
        'alert_tier': t.alert_tier,
    }

def emotional_log_to_dict(e):
    logger.info(f"Executing emotional_log_to_dict")
    logger.debug(f'Entering emotional_log_to_dict {getattr(request, "method", "") if "request" in locals() else ""}')
    return {
        'id': e.id, 'timestamp': e.timestamp.isoformat(),
        'emotion': e.emotion, 'sentiment_score': e.sentiment_score,
        'risk_level': e.risk_level, 'energy_level': e.energy_level,
        'query': e.query, 'response': e.response, 'reasoning': e.reasoning,
    }

def crisis_to_dict(c):
    logger.info(f"Executing crisis_to_dict")
    logger.debug(f'Entering crisis_to_dict {getattr(request, "method", "") if "request" in locals() else ""}')
    return {
        'id': c.id, 'timestamp': c.timestamp.isoformat(),
        'risk_level': c.risk_level, 'trigger_text': c.trigger_text,
        'action_taken': c.action_taken, 'acknowledged': c.acknowledged,
    }


# ─── Routines ─────────────────────────────────────────────────────────────────

@csrf_exempt
@require_http_methods(["GET", "POST"])
def routines(request):
    logger.info(f"Executing routines")
    logger.debug(f"Request method: {request.method}")
    logger.debug(f'Entering routines {getattr(request, "method", "") if "request" in locals() else ""}')
    if request.method == "GET":
        return JsonResponse([routine_to_dict(r) for r in Routine.objects.all()], safe=False)
    data = json.loads(request.body)
    r = Routine.objects.create(
        title=data['title'], time=data['time'],
        category=data['category'], alert_tier=data.get('alert_tier', 1),
    )
    return JsonResponse({'id': r.id})

@csrf_exempt
@require_http_methods(["DELETE"])
def routine_detail(request, pk):
    logger.info(f"Executing routine_detail")
    logger.debug(f"Request method: {request.method}")
    logger.debug(f'Entering routine_detail {getattr(request, "method", "") if "request" in locals() else ""}')
    Routine.objects.filter(pk=pk).delete()
    return JsonResponse({'success': True})


# ─── Events / Logs ────────────────────────────────────────────────────────────

@csrf_exempt
@require_http_methods(["GET", "POST"])
def events(request):
    logger.info(f"Executing events")
    logger.debug(f"Request method: {request.method}")
    logger.debug(f'Entering events {getattr(request, "method", "") if "request" in locals() else ""}')
    if request.method == "GET":
        logs = LogEntry.objects.all()[:100]
        return JsonResponse([log_to_dict(l) for l in logs], safe=False)
    data = json.loads(request.body)
    l = LogEntry.objects.create(
        event_type=data['event_type'],
        details=data.get('details', ''),
        alert_tier=data.get('alert_tier', 1),
    )
    return JsonResponse({'id': l.id})


# ─── Memory Facts ─────────────────────────────────────────────────────────────

@csrf_exempt
@require_http_methods(["GET", "POST"])
def memory(request):
    logger.info(f"Executing memory")
    logger.debug(f"Request method: {request.method}")
    logger.debug(f'Entering memory {getattr(request, "method", "") if "request" in locals() else ""}')
    if request.method == "GET":
        return JsonResponse([fact_to_dict(f) for f in MemoryFact.objects.all()], safe=False)
    data = json.loads(request.body)
    f = MemoryFact.objects.create(
        category=data['category'], fact=data['fact'],
        details=data.get('details', ''),
        image_url=data.get('image_url'),
    )
    return JsonResponse({'id': f.id})

@csrf_exempt
@require_http_methods(["DELETE"])
def memory_detail(request, pk):
    logger.info(f"Executing memory_detail")
    logger.debug(f"Request method: {request.method}")
    logger.debug(f'Entering memory_detail {getattr(request, "method", "") if "request" in locals() else ""}')
    MemoryFact.objects.filter(pk=pk).delete()
    return JsonResponse({'success': True})


# ─── Habits ───────────────────────────────────────────────────────────────────

@csrf_exempt
@require_http_methods(["GET", "POST"])
def habits(request):
    logger.info(f"Executing habits")
    logger.debug(f"Request method: {request.method}")
    logger.debug(f'Entering habits {getattr(request, "method", "") if "request" in locals() else ""}')
    if request.method == "GET":
        return JsonResponse([habit_to_dict(h) for h in Habit.objects.all()], safe=False)
    data = json.loads(request.body)
    today = date.today().isoformat()
    h = Habit.objects.create(
        title=data['title'], type=data['type'],
        target_count=data.get('target_count', 1),
        category=data.get('category', ''),
        last_reset_date=today,
    )
    return JsonResponse({'id': h.id})

@csrf_exempt
@require_http_methods(["DELETE"])
def habit_detail(request, pk):
    logger.info(f"Executing habit_detail")
    logger.debug(f"Request method: {request.method}")
    logger.debug(f'Entering habit_detail {getattr(request, "method", "") if "request" in locals() else ""}')
    Habit.objects.filter(pk=pk).delete()
    return JsonResponse({'success': True})

@csrf_exempt
@require_http_methods(["PUT"])
def habit_increment(request, pk):
    logger.info(f"Executing habit_increment")
    logger.debug(f"Request method: {request.method}")
    logger.debug(f'Entering habit_increment {getattr(request, "method", "") if "request" in locals() else ""}')
    today = date.today().isoformat()
    try:
        h = Habit.objects.get(pk=pk)
    except Habit.DoesNotExist:
        return JsonResponse({'error': 'Not found'}, status=404)
    new_count = 1 if h.last_reset_date != today else h.current_count + 1
    h.current_count = new_count
    h.last_reset_date = today
    h.save()
    return JsonResponse({'success': True, 'newCount': new_count})


# ─── Tasks ────────────────────────────────────────────────────────────────────

@csrf_exempt
@require_http_methods(["GET", "POST"])
def tasks(request):
    logger.info(f"Executing tasks")
    logger.debug(f"Request method: {request.method}")
    logger.debug(f'Entering tasks {getattr(request, "method", "") if "request" in locals() else ""}')
    if request.method == "GET":
        return JsonResponse([task_to_dict(t) for t in Task.objects.all()], safe=False)
    data = json.loads(request.body)
    t = Task.objects.create(
        title=data['title'], due_date=data.get('due_date'),
        category=data.get('category', ''),
        alert_tier=data.get('alert_tier', 1),
    )
    return JsonResponse({'id': t.id})

@csrf_exempt
@require_http_methods(["DELETE"])
def task_detail(request, pk):
    logger.info(f"Executing task_detail")
    logger.debug(f"Request method: {request.method}")
    logger.debug(f'Entering task_detail {getattr(request, "method", "") if "request" in locals() else ""}')
    Task.objects.filter(pk=pk).delete()
    return JsonResponse({'success': True})

@csrf_exempt
@require_http_methods(["PUT"])
def task_complete(request, pk):
    logger.info(f"Executing task_complete")
    logger.debug(f"Request method: {request.method}")
    logger.debug(f'Entering task_complete {getattr(request, "method", "") if "request" in locals() else ""}')
    Task.objects.filter(pk=pk).update(completed=True)
    return JsonResponse({'success': True})


# ─── Emotional Logs ───────────────────────────────────────────────────────────

@csrf_exempt
@require_http_methods(["GET", "POST"])
def emotional_logs(request):
    logger.info(f"Executing emotional_logs")
    logger.debug(f"Request method: {request.method}")
    logger.debug(f'Entering emotional_logs {getattr(request, "method", "") if "request" in locals() else ""}')
    if request.method == "GET":
        logs = EmotionalLog.objects.all()[:100]
        return JsonResponse([emotional_log_to_dict(l) for l in logs], safe=False)
    data = json.loads(request.body)
    l = EmotionalLog.objects.create(
        emotion=data.get('emotion', ''),
        sentiment_score=data.get('sentiment_score', 0.0),
        risk_level=data.get('risk_level', 'low'),
        energy_level=data.get('energy_level', ''),
        query=data.get('query', ''),
        response=data.get('response', ''),
        reasoning=data.get('reasoning', ''),
    )
    return JsonResponse({'id': l.id})


# ─── Crisis Events ────────────────────────────────────────────────────────────

@csrf_exempt
@require_http_methods(["GET", "POST"])
def crisis_events(request):
    logger.info(f"Executing crisis_events")
    logger.debug(f"Request method: {request.method}")
    logger.debug(f'Entering crisis_events {getattr(request, "method", "") if "request" in locals() else ""}')
    if request.method == "GET":
        events = CrisisEvent.objects.all()[:50]
        return JsonResponse([crisis_to_dict(c) for c in events], safe=False)
    data = json.loads(request.body)
    c = CrisisEvent.objects.create(
        risk_level=data.get('risk_level', 'low'),
        trigger_text=data.get('trigger_text', ''),
        action_taken=data.get('action_taken', ''),
    )
    return JsonResponse({'id': c.id})

@csrf_exempt
@require_http_methods(["PUT"])
def crisis_acknowledge(request, pk):
    logger.info(f"Executing crisis_acknowledge")
    logger.debug(f"Request method: {request.method}")
    logger.debug(f'Entering crisis_acknowledge {getattr(request, "method", "") if "request" in locals() else ""}')
    CrisisEvent.objects.filter(pk=pk).update(acknowledged=True)
    return JsonResponse({'success': True})


# ─── AI Endpoints ─────────────────────────────────────────────────────────────

@csrf_exempt
@require_http_methods(["POST"])
def ai_query(request):
    logger.info(f"Executing ai_query")
    logger.debug(f"Request method: {request.method}")
    logger.debug(f'Entering ai_query {getattr(request, "method", "") if "request" in locals() else ""}')
    """Main AI query endpoint — replaces the JS queryMemory() call."""
    data = json.loads(request.body)

    facts = [fact_to_dict(f) for f in MemoryFact.objects.all()]
    routines_list = [routine_to_dict(r) for r in Routine.objects.all()]
    habits_list = [habit_to_dict(h) for h in Habit.objects.all()]
    tasks_list = [task_to_dict(t) for t in Task.objects.all()]
    emotional_list = [emotional_log_to_dict(e) for e in EmotionalLog.objects.all()[:10]]

    try:
        result = gemini.query_memory(
            query=data.get('query', ''),
            facts=facts,
            history=data.get('history', []),
            routines=routines_list,
            completed_routine_ids=data.get('completedRoutineIds', []),
            habits=habits_list,
            tasks=tasks_list,
            emotional_logs=emotional_list,
            audio_data=data.get('audioData'),
        )
        return JsonResponse(result)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def ai_tts(request):
    logger.info(f"Executing ai_tts")
    logger.debug(f"Request method: {request.method}")
    logger.debug(f'Entering ai_tts {getattr(request, "method", "") if "request" in locals() else ""}')
    """TTS endpoint — returns base64 PCM audio."""
    data = json.loads(request.body)
    text = data.get('text', '')
    try:
        audio_b64 = gemini.generate_speech(text)
        if audio_b64:
            return JsonResponse({'audio': audio_b64})
        return JsonResponse({'audio': None})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def ai_tip(request):
    logger.info(f"Executing ai_tip")
    logger.debug(f"Request method: {request.method}")
    logger.debug(f'Entering ai_tip {getattr(request, "method", "") if "request" in locals() else ""}')
    """Helpful tip endpoint."""
    tip = gemini.get_helpful_tip()
    return JsonResponse({'tip': tip})
