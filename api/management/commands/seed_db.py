from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from api.models import Organization, User, Task

class Command(BaseCommand):
    help = "Seed the database with sample organizations, users, and tasks"

    def handle(self, *args, **options):
        self.stdout.write("Seeding database...")

        org1, created = Organization.objects.get_or_create(
            name="Rzabka",
            defaults={"created_at": timezone.now()}
        )
        org2, created = Organization.objects.get_or_create(
            name="Diino",
            defaults={"created_at": timezone.now()}
        )
        org3, created = Organization.objects.get_or_create(
            name="Bierdonka",
            defaults={"created_at": timezone.now()}
        )
        org4, created = Organization.objects.get_or_create(
            name="Kebabkrul",
            defaults={"created_at": timezone.now()}
        )


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
            
        user4, created = User.objects.get_or_create(
            username="zygmunt",
            defaults={
                "organization": org3,
                "email": "zygmunt@Bierdonka.com",
                "is_active": True,
            }
        )
        if created:
            user4.set_password("password123")
            user4.save()
            
        user5, created = User.objects.get_or_create(
            username="andrzej",
            defaults={
                "organization": org4,
                "email": "pawel@Bierdonka.com",
                "is_active": True,
            }
        )
        if created:
            user5.set_password("password123")
            user5.save()
        user6, created = User.objects.get_or_create(
            username="szymon",
            defaults={
                "organization": org4,
                "email": "szymon@kebabkrul.com",
                "is_active": True,
            }
        )
        if created:
            user6.set_password("password123")
            user6.save()

        now = timezone.now()
        Task.objects.get_or_create(
            title="Design new product",
            defaults={
                "description": "Create an alluring product",
                "completed": False,
                "assigned_to": user1,
                "organization": user1.organization,
                "deadline_datetime_with_tz": now + timedelta(days=7),
                "priority": 1,
                "created_at": now,
            }
        )
        
        Task.objects.get_or_create(
            title="Fix login bug",
            defaults={
                "description": "Users cannot reset their passwords",
                "completed": False,
                "assigned_to": user2,
                "organization": user2.organization,
                "deadline_datetime_with_tz": now + timedelta(days=3),
                "priority": 0,
                "created_at": now,
            }
        )
        
        Task.objects.get_or_create(
            title="Create more kebabs",
            defaults={
                "description": "more and more kebabs",
                "completed": True,
                "assigned_to": user3,
                "organization": user3.organization,
                "deadline_datetime_with_tz": now + timedelta(days=14),
                "priority": 2,
                "created_at": now,
            }
        )
        
        Task.objects.get_or_create(
            title="create 1000 memes",
            defaults={
                "description": "memememe",
                "completed": False,
                "assigned_to": user1,
                "organization": org1,
                "deadline_datetime_with_tz": now + timedelta(days=7),
                "priority": 1,
                "created_at": now,
            }
        )

        Task.objects.get_or_create(
            title="Eat kebabs",
            defaults={
                "description": "eat more",
                "completed": False,
                "assigned_to": user3,
                "organization": user3.organization,
                "deadline_datetime_with_tz": now + timedelta(hours=48),
                "priority": 3,
                "created_at": now,
            }
        )

        Task.objects.get_or_create(
            title="Read pan tadeusz",
            defaults={
                "description": "whole book",
                "completed": True,
                "assigned_to": user5,
                "organization": user5.organization,
                "deadline_datetime_with_tz": now + timedelta(minutes=60),
                "priority": 4, # Highest priority, even though completed
                "created_at": now,
            }
        )
        Task.objects.get_or_create(
            title="do something",
            defaults={
                "description": "idk",
                "completed": False,
                "assigned_to": user6,
                "organization": user6.organization,
                "deadline_datetime_with_tz": now + timedelta(weeks=2),
                "priority": 1,
                "created_at": now,
            }
        )

        Task.objects.get_or_create(
            title="ai generated title",
            defaults={
                "description": "something",
                "completed": False,
                "assigned_to": user6,
                "organization": user6.organization,
                "deadline_datetime_with_tz": now + timedelta(days=5),
                "priority": 3,
                "created_at": now,
            }
        )

        Task.objects.get_or_create(
            title="ask claude",
            defaults={
                "description": "yeah",
                "completed": True,
                "assigned_to": user5,
                "organization": user5.organization,
                "deadline_datetime_with_tz": now - timedelta(days=1), # A task completed yesterday
                "priority": 4, 
                "created_at": now - timedelta(days=2),
            }
        )

        self.stdout.write(
            self.style.SUCCESS("Database seeded")
        )
