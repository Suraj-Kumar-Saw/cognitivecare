from datetime import date
from django.core.management.base import BaseCommand
from care.models import Routine, MemoryFact, Habit, Task


class Command(BaseCommand):
    help = 'Seed the database with initial demo data'

    def handle(self, *args, **options):
        if Routine.objects.exists():
            self.stdout.write('Database already seeded. Skipping.')
            return

        today = date.today().isoformat()

        routines = [
            ('Breakfast', '08:00', 'Nutrition', 2),
            ('Morning Medication', '09:00', 'Medication', 2),
            ('Cognitive Activity', '10:30', 'Social', 1),
            ('Lunch', '12:30', 'Nutrition', 2),
            ('Light Exercise', '15:00', 'Physical Activity', 1),
            ('Evening Medication', '21:00', 'Medication', 2),
        ]
        for title, time, cat, tier in routines:
            Routine.objects.create(title=title, time=time, category=cat, alert_tier=tier)

        facts = [
            ('Identity', 'My Name', 'Your name is Arthur Miller.', None),
            ('Family', 'Daughter', 'Your daughter is Sarah. She lives in Chicago and calls every Sunday.', 'https://picsum.photos/seed/daughter/400/400'),
            ('Medication', 'Aricept', 'You take Aricept once a day in the morning for your memory.', None),
            ('Preference', 'Tea', 'You prefer Earl Grey tea with a little bit of honey.', None),
        ]
        for cat, fact, details, img in facts:
            MemoryFact.objects.create(category=cat, fact=fact, details=details, image_url=img)

        Habit.objects.create(title='Drink Water', type='build', target_count=5, current_count=0, category='Nutrition', last_reset_date=today)
        Habit.objects.create(title='Smoking', type='break', target_count=3, current_count=0, category='Health', last_reset_date=today)

        Task.objects.create(title='Doctor Appointment', due_date=today, category='Health', alert_tier=3)
        Task.objects.create(title='Call Sarah', due_date=today, category='Social', alert_tier=1)

        self.stdout.write(self.style.SUCCESS('Database seeded successfully.'))
