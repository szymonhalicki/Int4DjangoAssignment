from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from api.models import Organization, User, Task

class Command(BaseCommand):
    help = "Seed the database with sample organizations, users, and tasks"

    def handle(self, *args, **options):
        self.stdout.write("Seeding database...")

        # Create organizations
        org1, created = Organization.objects.get_or_create(
            name="Rzabka",
            defaults={"created_at": timezone.now()}
        )
        org2, created = Organization.objects.get_or_create(
            name="Diino",
            defaults={"created_at": timezone.now()}
        )

        self.stdout.write(f"Organizations: {org1.name}, {org2.name}")

        # Create users
        user1, created = User.objects.get_or_create(
            username="janusz",
            defaults={
                "organization": org1,
                "email": "janusz@rzabka.com",
                "is_active": True,
            }
        )
        if created:
            user1.set_password("password123")
            user1.save()

        user2, created = User.objects.get_or_create(
            username="grazyna",
            defaults={
                "organization": org1,
                "email": "grazyna@rzabka.com",
                "is_active": True,
            }
        )
        if created:
            user2.set_password("password123")
            user2.save()

        user3, created = User.objects.get_or_create(
            username="pawel",
            defaults={
                "organization": org2,
                "email": "pawel@diino.com",
                "is_active": True,
            }
        )
        if created:
            user3.set_password("password123")
            user3.save()

        self.stdout.write(f"Users: {user1.username}, {user2.username}, {user3.username}")

        # Create tasks
        now = timezone.now()
        task1, created = Task.objects.get_or_create(
            title="Design new product",
            defaults={
                "description": "Create an alluring product",
                "completed": False,
                "assigned_to": user1,
                "organization": org1,
                "deadline_datetime_with_tz": now + timedelta(days=7),
                "priority": 1,
                "created_at": now,
            }
        )

        task2, created = Task.objects.get_or_create(
            title="Fix login bug",
            defaults={
                "description": "Users cannot reset their passwords",
                "completed": False,
                "assigned_to": user2,
                "organization": org1,
                "deadline_datetime_with_tz": now + timedelta(days=3),
                "priority": 0,
                "created_at": now,
            }
        )

        task3, created = Task.objects.get_or_create(
            title="Prepare new newsletter",
            defaults={
                "description": "Create a Q4 newsletter with holiday offers",
                "completed": True,
                "assigned_to": user3,
                "organization": org2,
                "deadline_datetime_with_tz": now + timedelta(days=14),
                "priority": 2,
                "created_at": now,
            }
        )

        self.stdout.write(
            self.style.SUCCESS("✓ Database seeded successfully!")
        )
        self.stdout.write(f"Tasks created: {task1.title}, {task2.title}, {task3.title}")