from django.db import models


class Routine(models.Model):
    CATEGORY_CHOICES = [
        ('Medication', 'Medication'),
        ('Nutrition', 'Nutrition'),
        ('Social', 'Social'),
        ('Physical Activity', 'Physical Activity'),
        ('Other', 'Other'),
    ]
    title = models.CharField(max_length=200)
    time = models.CharField(max_length=5)  # HH:mm
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    alert_tier = models.IntegerField(default=1)
    recurrence = models.CharField(max_length=50, default='daily')
    last_triggered = models.CharField(max_length=20, null=True, blank=True)

    class Meta:
        ordering = ['time']

    def __str__(self):
        return f"{self.title} at {self.time}"


class MemoryFact(models.Model):
    CATEGORY_CHOICES = [
        ('Identity', 'Identity'),
        ('Family', 'Family'),
        ('Medication', 'Medication'),
        ('Preference', 'Preference'),
        ('Other', 'Other'),
    ]
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    fact = models.CharField(max_length=200)
    details = models.TextField()
    image_url = models.URLField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.category}: {self.fact}"


class LogEntry(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    event_type = models.CharField(max_length=100)
    details = models.TextField(blank=True)
    alert_tier = models.IntegerField(default=1)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.event_type} at {self.timestamp}"


class Habit(models.Model):
    TYPE_CHOICES = [('build', 'Build'), ('break', 'Break')]
    title = models.CharField(max_length=200)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    target_count = models.IntegerField(default=1)
    current_count = models.IntegerField(default=0)
    category = models.CharField(max_length=100, blank=True)
    last_reset_date = models.CharField(max_length=10)  # YYYY-MM-DD

    def __str__(self):
        return self.title


class Task(models.Model):
    CATEGORY_CHOICES = [
        ('Health', 'Health'),
        ('Social', 'Social'),
        ('Personal', 'Personal'),
        ('Other', 'Other'),
    ]
    title = models.CharField(max_length=200)
    due_date = models.CharField(max_length=10, null=True, blank=True)  # YYYY-MM-DD
    completed = models.BooleanField(default=False)
    category = models.CharField(max_length=100, blank=True)
    alert_tier = models.IntegerField(default=1)

    class Meta:
        ordering = ['due_date']

    def __str__(self):
        return self.title


class EmotionalLog(models.Model):
    RISK_CHOICES = [('low', 'Low'), ('medium', 'Medium'), ('high', 'High')]
    timestamp = models.DateTimeField(auto_now_add=True)
    emotion = models.CharField(max_length=100, blank=True)
    sentiment_score = models.FloatField(default=0.0)
    risk_level = models.CharField(max_length=10, choices=RISK_CHOICES, default='low')
    energy_level = models.CharField(max_length=50, blank=True)
    query = models.TextField(blank=True)
    response = models.TextField(blank=True)
    reasoning = models.TextField(blank=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.emotion} ({self.risk_level}) at {self.timestamp}"


class CrisisEvent(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    risk_level = models.CharField(max_length=20)
    trigger_text = models.TextField(blank=True)
    action_taken = models.TextField(blank=True)
    acknowledged = models.BooleanField(default=False)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"Crisis ({self.risk_level}) at {self.timestamp}"
