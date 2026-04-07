import json
import logging
from datetime import date, datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.shortcuts import render
from .models import Routine, MemoryFact, LogEntry, Habit, Task, EmotionalLog, CrisisEvent
from .services import gemini

logger = logging.getLogger(__name__)


# ─── Page Views ───────────────────────────────────────────────────────────────

def index(request):
    logger.info("Executing index")
    logger.debug(f"Request method: {request.method}")
    try:
        return render(request, 'care/index.html')
    except Exception as e:
        logger.error(f"Error rendering index: {e}", exc_info=True)
        return JsonResponse({'error': 'Internal server error'}, status=500)


# ─── Helpers ──────────────────────────────────────────────────────────────────

def routine_to_dict(r):
    return {
        'id': r.id, 'title': r.title, 'time': r.time,
        'category': r.category, 'alert_tier': r.alert_tier,
        'recurrence': r.recurrence, 'last_triggered': r.last_triggered,
    }

def fact_to_dict(f):
    return {
        'id': f.id, 'category': f.category, 'fact': f.fact,
        'details': f.details, 'image_url': f.image_url,
        'timestamp': f.timestamp.isoformat() if f.timestamp else None,
    }

def log_to_dict(l):
    return {
        'id': l.id, 'timestamp': l.timestamp.isoformat() if l.timestamp else None,
        'event_type': l.event_type, 'details': l.details,
        'alert_tier': l.alert_tier,
    }

def habit_to_dict(h):
    return {
        'id': h.id, 'title': h.title, 'type': h.type,
        'target_count': h.target_count, 'current_count': h.current_count,
        'category': h.category, 'last_reset_date': h.last_reset_date,
    }

def task_to_dict(t):
    return {
        'id': t.id, 'title': t.title, 'due_date': t.due_date,
        'completed': t.completed, 'category': t.category,
        'alert_tier': t.alert_tier,
    }

def emotional_log_to_dict(e):
    return {
        'id': e.id, 'timestamp': e.timestamp.isoformat() if e.timestamp else None,
        'emotion': e.emotion, 'sentiment_score': e.sentiment_score,
        'risk_level': e.risk_level, 'energy_level': e.energy_level,
        'query': e.query, 'response': e.response, 'reasoning': e.reasoning,
    }

def crisis_to_dict(c):
    return {
        'id': c.id, 'timestamp': c.timestamp.isoformat() if c.timestamp else None,
        'risk_level': c.risk_level, 'trigger_text': c.trigger_text,
        'action_taken': c.action_taken, 'acknowledged': c.acknowledged,
    }


# ─── Routines ─────────────────────────────────────────────────────────────────

@csrf_exempt
@require_http_methods(["GET", "POST"])
def routines(request):
    logger.info("Executing routines")
    logger.debug(f"Request method: {request.method}")
    try:
        if request.method == "GET":
            return JsonResponse([routine_to_dict(r) for r in Routine.objects.all()], safe=False)

        data = json.loads(request.body)
        r = Routine.objects.create(
            title=data['title'], time=data['time'],
            category=data['category'], alert_tier=data.get('alert_tier', 1),
        )
        logger.info(f"Routine created with id {r.id}")
        return JsonResponse({'id': r.id})
    except json.JSONDecodeError as e:
        logger.warning(f"Invalid JSON in routines request: {e}")
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except KeyError as e:
        logger.warning(f"Missing required field in routines: {e}")
        return JsonResponse({'error': f'Missing field: {e}'}, status=400)
    except Exception as e:
        logger.error(f"Error in routines endpoint: {e}", exc_info=True)
        return JsonResponse({'error': 'Internal server error'}, status=500)

@csrf_exempt
@require_http_methods(["DELETE"])
def routine_detail(request, pk):
    logger.info(f"Executing routine_detail for pk {pk}")
    logger.debug(f"Request method: {request.method}")
    try:
        deleted, _ = Routine.objects.filter(pk=pk).delete()
        if deleted == 0:
            logger.warning(f"Routine {pk} not found for deletion")
            return JsonResponse({'error': 'Not found'}, status=404)
        logger.info(f"Routine {pk} deleted")
        return JsonResponse({'success': True})
    except Exception as e:
        logger.error(f"Error in routine_detail endpoint: {e}", exc_info=True)
        return JsonResponse({'error': 'Internal server error'}, status=500)


# ─── Events / Logs ────────────────────────────────────────────────────────────

@csrf_exempt
@require_http_methods(["GET", "POST"])
def events(request):
    logger.info("Executing events")
    logger.debug(f"Request method: {request.method}")
    try:
        if request.method == "GET":
            logs = LogEntry.objects.all()[:100]
            return JsonResponse([log_to_dict(l) for l in logs], safe=False)

        data = json.loads(request.body)
        l = LogEntry.objects.create(
            event_type=data['event_type'],
            details=data.get('details', ''),
            alert_tier=data.get('alert_tier', 1),
        )
        logger.info(f"LogEntry created with id {l.id}")
        return JsonResponse({'id': l.id})
    except json.JSONDecodeError as e:
        logger.warning(f"Invalid JSON in events request: {e}")
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except KeyError as e:
        logger.warning(f"Missing required field in events: {e}")
        return JsonResponse({'error': f'Missing field: {e}'}, status=400)
    except Exception as e:
        logger.error(f"Error in events endpoint: {e}", exc_info=True)
        return JsonResponse({'error': 'Internal server error'}, status=500)


# ─── Memory Facts ─────────────────────────────────────────────────────────────

@csrf_exempt
@require_http_methods(["GET", "POST"])
def memory(request):
    logger.info("Executing memory")
    logger.debug(f"Request method: {request.method}")
    try:
        if request.method == "GET":
            return JsonResponse([fact_to_dict(f) for f in MemoryFact.objects.all()], safe=False)

        data = json.loads(request.body)
        f = MemoryFact.objects.create(
            category=data['category'], fact=data['fact'],
            details=data.get('details', ''),
            image_url=data.get('image_url'),
        )
        logger.info(f"MemoryFact created with id {f.id}")
        return JsonResponse({'id': f.id})
    except json.JSONDecodeError as e:
        logger.warning(f"Invalid JSON in memory request: {e}")
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except KeyError as e:
        logger.warning(f"Missing required field in memory: {e}")
        return JsonResponse({'error': f'Missing field: {e}'}, status=400)
    except Exception as e:
        logger.error(f"Error in memory endpoint: {e}", exc_info=True)
        return JsonResponse({'error': 'Internal server error'}, status=500)

@csrf_exempt
@require_http_methods(["DELETE"])
def memory_detail(request, pk):
    logger.info(f"Executing memory_detail for pk {pk}")
    logger.debug(f"Request method: {request.method}")
    try:
        deleted, _ = MemoryFact.objects.filter(pk=pk).delete()
        if deleted == 0:
            logger.warning(f"MemoryFact {pk} not found for deletion")
            return JsonResponse({'error': 'Not found'}, status=404)
        logger.info(f"MemoryFact {pk} deleted")
        return JsonResponse({'success': True})
    except Exception as e:
        logger.error(f"Error in memory_detail endpoint: {e}", exc_info=True)
        return JsonResponse({'error': 'Internal server error'}, status=500)


# ─── Habits ───────────────────────────────────────────────────────────────────

@csrf_exempt
@require_http_methods(["GET", "POST"])
def habits(request):
    logger.info("Executing habits")
    logger.debug(f"Request method: {request.method}")
    try:
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
        logger.info(f"Habit created with id {h.id}")
        return JsonResponse({'id': h.id})
    except json.JSONDecodeError as e:
        logger.warning(f"Invalid JSON in habits request: {e}")
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except KeyError as e:
        logger.warning(f"Missing required field in habits: {e}")
        return JsonResponse({'error': f'Missing field: {e}'}, status=400)
    except Exception as e:
        logger.error(f"Error in habits endpoint: {e}", exc_info=True)
        return JsonResponse({'error': 'Internal server error'}, status=500)

@csrf_exempt
@require_http_methods(["DELETE"])
def habit_detail(request, pk):
    logger.info(f"Executing habit_detail for pk {pk}")
    logger.debug(f"Request method: {request.method}")
    try:
        deleted, _ = Habit.objects.filter(pk=pk).delete()
        if deleted == 0:
            logger.warning(f"Habit {pk} not found for deletion")
            return JsonResponse({'error': 'Not found'}, status=404)
        logger.info(f"Habit {pk} deleted")
        return JsonResponse({'success': True})
    except Exception as e:
        logger.error(f"Error in habit_detail endpoint: {e}", exc_info=True)
        return JsonResponse({'error': 'Internal server error'}, status=500)

@csrf_exempt
@require_http_methods(["PUT"])
def habit_increment(request, pk):
    logger.info(f"Executing habit_increment for pk {pk}")
    logger.debug(f"Request method: {request.method}")
    try:
        today = date.today().isoformat()
        h = Habit.objects.get(pk=pk)
        new_count = 1 if h.last_reset_date != today else h.current_count + 1
        h.current_count = new_count
        h.last_reset_date = today
        h.save()
        logger.info(f"Habit {pk} incremented to {new_count}")
        return JsonResponse({'success': True, 'newCount': new_count})
    except Habit.DoesNotExist:
        logger.warning(f"Habit {pk} not found for increment")
        return JsonResponse({'error': 'Not found'}, status=404)
    except Exception as e:
        logger.error(f"Error in habit_increment endpoint: {e}", exc_info=True)
        return JsonResponse({'error': 'Internal server error'}, status=500)


# ─── Tasks ────────────────────────────────────────────────────────────────────

@csrf_exempt
@require_http_methods(["GET", "POST"])
def tasks(request):
    logger.info("Executing tasks")
    logger.debug(f"Request method: {request.method}")
    try:
        if request.method == "GET":
            return JsonResponse([task_to_dict(t) for t in Task.objects.all()], safe=False)

        data = json.loads(request.body)
        t = Task.objects.create(
            title=data['title'], due_date=data.get('due_date'),
            category=data.get('category', ''),
            alert_tier=data.get('alert_tier', 1),
        )
        logger.info(f"Task created with id {t.id}")
        return JsonResponse({'id': t.id})
    except json.JSONDecodeError as e:
        logger.warning(f"Invalid JSON in tasks request: {e}")
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except KeyError as e:
        logger.warning(f"Missing required field in tasks: {e}")
        return JsonResponse({'error': f'Missing field: {e}'}, status=400)
    except Exception as e:
        logger.error(f"Error in tasks endpoint: {e}", exc_info=True)
        return JsonResponse({'error': 'Internal server error'}, status=500)

@csrf_exempt
@require_http_methods(["DELETE"])
def task_detail(request, pk):
    logger.info(f"Executing task_detail for pk {pk}")
    logger.debug(f"Request method: {request.method}")
    try:
        deleted, _ = Task.objects.filter(pk=pk).delete()
        if deleted == 0:
            logger.warning(f"Task {pk} not found for deletion")
            return JsonResponse({'error': 'Not found'}, status=404)
        logger.info(f"Task {pk} deleted")
        return JsonResponse({'success': True})
    except Exception as e:
        logger.error(f"Error in task_detail endpoint: {e}", exc_info=True)
        return JsonResponse({'error': 'Internal server error'}, status=500)

@csrf_exempt
@require_http_methods(["PUT"])
def task_complete(request, pk):
    logger.info(f"Executing task_complete for pk {pk}")
    logger.debug(f"Request method: {request.method}")
    try:
        updated = Task.objects.filter(pk=pk).update(completed=True)
        if updated == 0:
            logger.warning(f"Task {pk} not found for completion")
            return JsonResponse({'error': 'Not found'}, status=404)
        logger.info(f"Task {pk} marked complete")
        return JsonResponse({'success': True})
    except Exception as e:
        logger.error(f"Error in task_complete endpoint: {e}", exc_info=True)
        return JsonResponse({'error': 'Internal server error'}, status=500)


# ─── Emotional Logs ───────────────────────────────────────────────────────────

@csrf_exempt
@require_http_methods(["GET", "POST"])
def emotional_logs(request):
    logger.info("Executing emotional_logs")
    logger.debug(f"Request method: {request.method}")
    try:
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
        logger.info(f"EmotionalLog created with id {l.id}")
        return JsonResponse({'id': l.id})
    except json.JSONDecodeError as e:
        logger.warning(f"Invalid JSON in emotional_logs request: {e}")
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Error in emotional_logs endpoint: {e}", exc_info=True)
        return JsonResponse({'error': 'Internal server error'}, status=500)


# ─── Crisis Events ────────────────────────────────────────────────────────────

@csrf_exempt
@require_http_methods(["GET", "POST"])
def crisis_events(request):
    logger.info("Executing crisis_events")
    logger.debug(f"Request method: {request.method}")
    try:
        if request.method == "GET":
            events = CrisisEvent.objects.all()[:50]
            return JsonResponse([crisis_to_dict(c) for c in events], safe=False)

        data = json.loads(request.body)
        c = CrisisEvent.objects.create(
            risk_level=data.get('risk_level', 'low'),
            trigger_text=data.get('trigger_text', ''),
            action_taken=data.get('action_taken', ''),
        )
        logger.info(f"CrisisEvent created with id {c.id}")
        return JsonResponse({'id': c.id})
    except json.JSONDecodeError as e:
        logger.warning(f"Invalid JSON in crisis_events request: {e}")
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Error in crisis_events endpoint: {e}", exc_info=True)
        return JsonResponse({'error': 'Internal server error'}, status=500)

@csrf_exempt
@require_http_methods(["PUT"])
def crisis_acknowledge(request, pk):
    logger.info(f"Executing crisis_acknowledge for pk {pk}")
    logger.debug(f"Request method: {request.method}")
    try:
        updated = CrisisEvent.objects.filter(pk=pk).update(acknowledged=True)
        if updated == 0:
            logger.warning(f"CrisisEvent {pk} not found for acknowledgement")
            return JsonResponse({'error': 'Not found'}, status=404)
        logger.info(f"CrisisEvent {pk} acknowledged")
        return JsonResponse({'success': True})
    except Exception as e:
        logger.error(f"Error in crisis_acknowledge endpoint: {e}", exc_info=True)
        return JsonResponse({'error': 'Internal server error'}, status=500)


# ─── AI Endpoints ─────────────────────────────────────────────────────────────

@csrf_exempt
@require_http_methods(["POST"])
def ai_query(request):
    logger.info("Executing ai_query")
    logger.debug(f"Request method: {request.method}")
    try:
        data = json.loads(request.body)

        facts = [fact_to_dict(f) for f in MemoryFact.objects.all()]
        routines_list = [routine_to_dict(r) for r in Routine.objects.all()]
        habits_list = [habit_to_dict(h) for h in Habit.objects.all()]
        tasks_list = [task_to_dict(t) for t in Task.objects.all()]
        emotional_list = [emotional_log_to_dict(e) for e in EmotionalLog.objects.all()[:10]]

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
        logger.info("Successfully executed ai_query")
        return JsonResponse(result)
    except json.JSONDecodeError as e:
        logger.warning(f"Invalid JSON in ai_query request: {e}")
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Error in ai_query endpoint: {e}", exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def ai_tts(request):
    logger.info("Executing ai_tts")
    logger.debug(f"Request method: {request.method}")
    try:
        data = json.loads(request.body)
        text = data.get('text', '')
        if not text:
            logger.warning("Empty text provided for ai_tts")
            return JsonResponse({'audio': None})

        audio_b64 = gemini.generate_speech(text)
        if audio_b64:
            logger.info("Successfully generated TTS audio")
            return JsonResponse({'audio': audio_b64})

        logger.warning("TTS audio generation returned None")
        return JsonResponse({'audio': None})
    except json.JSONDecodeError as e:
        logger.warning(f"Invalid JSON in ai_tts request: {e}")
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Error in ai_tts endpoint: {e}", exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def ai_tip(request):
    logger.info("Executing ai_tip")
    logger.debug(f"Request method: {request.method}")
    try:
        tip = gemini.get_helpful_tip()
        logger.info("Successfully retrieved AI tip")
        return JsonResponse({'tip': tip})
    except Exception as e:
        logger.error(f"Error in ai_tip endpoint: {e}", exc_info=True)
        return JsonResponse({'error': 'Internal server error'}, status=500)
