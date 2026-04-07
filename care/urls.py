from django.urls import path
from . import views

urlpatterns = [
    # Pages
    path('', views.index, name='index'),

    # Routines
    path('api/routines', views.routines, name='routines'),
    path('api/routines/<int:pk>', views.routine_detail, name='routine-detail'),

    # Events / Logs
    path('api/events', views.events, name='events'),

    # Memory Facts
    path('api/memory', views.memory, name='memory'),
    path('api/memory/<int:pk>', views.memory_detail, name='memory-detail'),

    # Habits
    path('api/habits', views.habits, name='habits'),
    path('api/habits/<int:pk>', views.habit_detail, name='habit-detail'),
    path('api/habits/<int:pk>/increment', views.habit_increment, name='habit-increment'),

    # Tasks
    path('api/tasks', views.tasks, name='tasks'),
    path('api/tasks/<int:pk>', views.task_detail, name='task-detail'),
    path('api/tasks/<int:pk>/complete', views.task_complete, name='task-complete'),

    # Emotional Logs
    path('api/emotional_logs', views.emotional_logs, name='emotional-logs'),

    # Crisis Events
    path('api/crisis_events', views.crisis_events, name='crisis-events'),
    path('api/crisis_events/<int:pk>/acknowledge', views.crisis_acknowledge, name='crisis-acknowledge'),

    # AI
    path('api/ai/query', views.ai_query, name='ai-query'),
    path('api/ai/tts', views.ai_tts, name='ai-tts'),
    path('api/ai/tip', views.ai_tip, name='ai-tip'),
]
