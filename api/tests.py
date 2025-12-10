from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import jwt
from django.conf import settings
from . import models, schemas
import json

User = get_user_model()

class JWTAuthenticationTests(TestCase):    
    def setUp(self):
        self.org = models.Organization.objects.create(name="Test Org")
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123",
            organization=self.org
        )
        self.client = Client() 
    
    def test_valid_token_generation(self):
        response = self.client.post(
            "/api/v1/auth/login",
            data=json.dumps({"username": "testuser", "password": "testpass123"}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("token", data)
        self.assertIn("expires", data)
    
    def test_invalid_credentials(self):
        response = self.client.post(
            "/api/v1/auth/login",
            data=json.dumps({"username": "testuser", "password": "wrongpassword"}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 401)
        self.assertIn("message", response.json())
    
    def test_nonexistent_user(self):
        response = self.client.post(
            "/api/v1/auth/login",
            data=json.dumps({"username": "nonexistent", "password": "testpass123"}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 401)
    
    def test_token_expiration(self):
        exp = timezone.now() - timedelta(hours=1)
        expired_token = jwt.encode(
            {"user_id": self.user.id, "exp": exp},
            settings.SECRET_KEY,
            algorithm="HS256"
        )
        response = self.client.get(
            "/api/v1/tasks",
            HTTP_AUTHORIZATION=f"Bearer {expired_token}"
        )
        self.assertEqual(response.status_code, 401)
    
    def test_malformed_token(self):
        response = self.client.get(
            "/api/v1/tasks",
            HTTP_AUTHORIZATION="Bearer malformed.token.here"
        )
        self.assertEqual(response.status_code, 401)
    
    def test_missing_authorization_header(self):
        response = self.client.get("/api/v1/tasks")
        self.assertEqual(response.status_code, 401)


class TaskAPITests(TestCase):
    def setUp(self):
        self.org1 = models.Organization.objects.create(name="Org 1")
        self.org2 = models.Organization.objects.create(name="Org 2")
        
        self.user1 = User.objects.create_user(
            username="user1",
            password="pass123",
            organization=self.org1
        )
        self.user2 = User.objects.create_user(
            username="user2",
            password="pass123",
            organization=self.org2
        )
        
        self.deadline = timezone.now() + timedelta(days=7)
        
        self.task1 = models.Task.objects.create(
            title="Task 1",
            description="Description 1",
            completed=False,
            assigned_to=self.user1,
            organization=self.org1,
            deadline_datetime_with_tz=self.deadline,
            priority=0
        )
        
        self.task2 = models.Task.objects.create(
            title="Task 2",
            description="Description 2",
            completed=False,
            assigned_to=self.user2,
            organization=self.org2,
            deadline_datetime_with_tz=self.deadline,
            priority=1
        )
        
        self.client = Client()
        
        exp = timezone.now() + timedelta(hours=8)
        self.token1 = jwt.encode(
            {"user_id": self.user1.id, "exp": exp},
            settings.SECRET_KEY,
            algorithm="HS256"
        )
        self.token2 = jwt.encode(
            {"user_id": self.user2.id, "exp": exp},
            settings.SECRET_KEY,
            algorithm="HS256"
        )
    
    def test_list_tasks_with_auth(self):
        response = self.client.get(
            "/api/v1/tasks",
            HTTP_AUTHORIZATION=f"Bearer {self.token1}"
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        results = data.get('items', data) if isinstance(data, dict) else data
        if isinstance(results, dict):
            results = results.get('results', [])
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], "Task 1")
    
    def test_list_tasks_without_auth(self):
        response = self.client.get("/api/v1/tasks")
        self.assertEqual(response.status_code, 401)
    
    def test_multi_tenancy(self):
        response1 = self.client.get(
            "/api/v1/tasks",
            HTTP_AUTHORIZATION=f"Bearer {self.token1}"
        )
        response2 = self.client.get(
            "/api/v1/tasks",
            HTTP_AUTHORIZATION=f"Bearer {self.token2}"
        )
        
        results1 = response1.json()['items']
        results2 = response2.json()['items']
        
        self.assertEqual(len(results1), 1)
        self.assertEqual(results1[0]['id'], self.task1.id)
        
        self.assertEqual(len(results2), 1)
        self.assertEqual(results2[0]['id'], self.task2.id)
    
    def test_create_task(self):
        response = self.client.post(
            "/api/v1/tasks",
            data=json.dumps({
                "title": "New Task",
                "description": "New Description",
                "completed": False,
                "assigned_to": self.user1.id,
                "deadline_datetime_with_tz": self.deadline.isoformat(),
                "priority": 0
            }),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {self.token1}"
        )
        self.assertEqual(response.status_code, 200)
    
    def test_create_task_with_user_from_different_org(self):
        response = self.client.post(
            "/api/v1/tasks",
            data=json.dumps({
                "title": "New Task",
                "description": "New Description",
                "completed": False,
                "assigned_to": self.user2.id,
                "deadline_datetime_with_tz": self.deadline.isoformat(),
                "priority": 0
            }),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {self.token1}"
        )
        self.assertEqual(response.status_code, 403)
    
    def test_create_task_without_auth(self):
        response = self.client.post(
            "/api/v1/tasks",
            data=json.dumps({
                "title": "New Task",
                "description": "New Description",
                "completed": False,
                "assigned_to": self.user1.id,
                "deadline_datetime_with_tz": self.deadline.isoformat(),
                "priority": 0
            }),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 401)
    
    def test_update_task(self):
        response = self.client.put(
            f"/api/v1/tasks/{self.task1.id}",
            data=json.dumps({
                "title": "Updated Task",
                "description": "Updated Description",
                "completed": True,
                "assigned_to": self.user1.id,
                "deadline_datetime_with_tz": self.deadline.isoformat(),
                "priority": 1
            }),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {self.token1}"
        )
        self.assertEqual(response.status_code, 200)
        refreshed_task = models.Task.objects.get(id=self.task1.id)
        self.assertEqual(refreshed_task.title, "Updated Task")
        self.assertTrue(refreshed_task.completed)
    
    def test_update_task_from_different_org(self):
        response = self.client.put(
            f"/api/v1/tasks/{self.task1.id}",
            data=json.dumps({
                "title": "Hacked",
                "description": "Hacked",
                "completed": False,
                "assigned_to": self.user2.id,
                "deadline_datetime_with_tz": self.deadline.isoformat(),
                "priority": 0
            }),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {self.token2}"
        )
        self.assertEqual(response.status_code, 404)
    
    def test_delete_task(self):
        response = self.client.delete(
            f"/api/v1/tasks/{self.task1.id}",
            HTTP_AUTHORIZATION=f"Bearer {self.token1}"
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(models.Task.objects.filter(id=self.task1.id).exists())
    
    def test_delete_task_from_different_org(self):
        response = self.client.delete(
            f"/api/v1/tasks/{self.task1.id}",
            HTTP_AUTHORIZATION=f"Bearer {self.token2}"
        )
        self.assertEqual(response.status_code, 404)
        self.assertTrue(models.Task.objects.filter(id=self.task1.id).exists())
        
    def test_pagination(self):
        models.Task.objects.bulk_create([
            models.Task(
                title="bulk1",
                description="pagination",
                completed=False,
                assigned_to=self.user1,
                organization=self.org1,
                deadline_datetime_with_tz=self.deadline,
                priority=0),
            models.Task(
                title="bulk2",
                description="pagination",
                completed=False,
                assigned_to=self.user1,
                organization=self.org1,
                deadline_datetime_with_tz=self.deadline,
                priority=0),
            models.Task(
                title="bulk3",
                description="pagination",
                completed=False,
                assigned_to=self.user1,
                organization=self.org1,
                deadline_datetime_with_tz=self.deadline,
                priority=0),
            models.Task(
                title="bulk4",
                description="pagination",
                completed=False,
                assigned_to=self.user1,
                organization=self.org1,
                deadline_datetime_with_tz=self.deadline,
                priority=0),
        ])
        
        response = self.client.get(
            "/api/v1/tasks?limit=2&offset=0",
            HTTP_AUTHORIZATION=f"Bearer {self.token1}"
        )
        
        data = response.json()
        
        self.assertEqual(len(data['items']), 2) 
        self.assertEqual(data['count'], 5)


class UserAPITests(TestCase):    
    def setUp(self):
        self.org = models.Organization.objects.create(name="Test Org")
        self.user = User.objects.create_user(
            username="testuser",
            password="pass123",
            organization=self.org
        )
        self.client = Client()
        
        exp = timezone.now() + timedelta(hours=8)
        self.token = jwt.encode(
            {"user_id": self.user.id, "exp": exp},
            settings.SECRET_KEY,
            algorithm="HS256"
        )
    
    def test_list_users(self):
        response = self.client.get(
            "/api/v1/users/",
            HTTP_AUTHORIZATION=f"Bearer {self.token}"
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        # in case pagination is added
        users = data.get('items', data) if isinstance(data, dict) else data
        if isinstance(users, dict):
            users = users.get('results', [])
        self.assertGreater(len(users), 0)
        self.assertTrue(any(u['username'] == 'testuser' for u in users))
    
    def test_list_users_without_auth(self):
        response = self.client.get("/api/v1/users/")
        self.assertEqual(response.status_code, 401)
    
    def test_create_user(self):
        response = self.client.post(
            "/api/v1/users/",
            data=json.dumps({"username": "newuser", "password": "newpass123"}),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {self.token}"
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.filter(username="newuser").exists())
    
    def test_create_duplicate_user(self):
        response = self.client.post(
            "/api/v1/users/",
            data=json.dumps({"username": "testuser", "password": "pass123"}),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {self.token}"
        )
        self.assertEqual(response.status_code, 400)
    
    def test_create_user_without_auth(self):
        response = self.client.post(
            "/api/v1/users/",
            data=json.dumps({"username": "newuser", "password": "newpass123"}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 401)
        
    def test_user_list_is_tenant_isolated(self):
        org2 = models.Organization.objects.create(name="B")
        u2 = User.objects.create_user(username="u2", password="p", organization=org2)
        u2 = User.objects.create_user(username="u3", password="p", organization=org2)
        token2 = jwt.encode({"user_id": u2.id, "exp": int((timezone.now()+timedelta(hours=8)).timestamp())}, settings.SECRET_KEY, algorithm="HS256")
        response1 = self.client.get(
            "/api/v1/users/", 
            HTTP_AUTHORIZATION=f"Bearer {self.token}")
        response2 = self.client.get(
            "/api/v1/users/", 
            HTTP_AUTHORIZATION=f"Bearer {token2}")
        data1 = response1.json()
        data2 = response2.json()
        usernames1 = [u['username'] for u in data1]
        usernames2 = [u['username'] for u in data2]
        
        self.assertTrue(all(u['organization']['id'] == self.org.id for u in data1))
        self.assertTrue(all(u['organization']['id'] == org2.id for u in data2))
        
        self.assertIn('testuser', usernames1)
        self.assertNotIn('u2', usernames1)
        self.assertNotIn('u3', usernames1)
        
        self.assertIn('u2', usernames2)
        self.assertIn('u3', usernames2) 
        self.assertNotIn('testuser', usernames2)
        


class SchemaValidationTests(TestCase):
    def setUp(self):
        self.org = models.Organization.objects.create(name="Test Org")
        self.user = User.objects.create_user(
            username="testuser",
            password="pass123",
            organization=self.org
        )
        self.client = Client()  # Changed: Use Django's Client instead of Ninja's TestClient
        
        exp = timezone.now() + timedelta(hours=8)
        self.token = jwt.encode(
            {"user_id": self.user.id, "exp": exp},
            settings.SECRET_KEY,
            algorithm="HS256"
        )
    
    def test_invalid_task_schema_missing_title(self):
        deadline = timezone.now() + timedelta(days=7)
        response = self.client.post(
            "/api/v1/tasks",
            data=json.dumps({
                "description": "Description",
                "completed": False,
                "assigned_to": self.user.id,
                "deadline_datetime_with_tz": deadline.isoformat(),
                "priority": 0
            }),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {self.token}"
        )
        self.assertEqual(response.status_code, 422)
    
    def test_invalid_task_schema_invalid_priority(self):
        deadline = timezone.now() + timedelta(days=7)
        response = self.client.post(
            "/api/v1/tasks",
            data=json.dumps({
                "title": "Task",
                "description": "Description",
                "completed": False,
                "assigned_to": self.user.id,
                "deadline_datetime_with_tz": deadline.isoformat(),
                "priority": "invalid"
            }),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {self.token}"
        )
        self.assertEqual(response.status_code, 422)
    
    def test_invalid_login_schema(self):
        response = self.client.post(
            "/api/v1/auth/login",
            data=json.dumps({"password": "pass123"}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 422)
    
    def test_valid_task_schema(self):
        deadline = timezone.now() + timedelta(days=7)
        response = self.client.post(
            "/api/v1/tasks",
            data=json.dumps({
                "title": "Valid Task",
                "description": "Valid Description",
                "completed": False,
                "assigned_to": self.user.id,
                "organization": self.org.id,
                "deadline_datetime_with_tz": deadline.isoformat(),
                "priority": 0
            }),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {self.token}"
        )
        self.assertEqual(response.status_code, 200)
    
    def test_valid_login_schema(self):
        response = self.client.post(
            "/api/v1/auth/login",
            data=json.dumps({"username": "testuser", "password": "pass123"}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)


class OrganizationModelTests(TestCase):
    def test_create_organization(self):
        org = models.Organization.objects.create(name="Test Org")
        self.assertEqual(org.name, "Test Org")
        self.assertIsNotNone(org.id)
    
    def test_organization_str(self):
        org = models.Organization.objects.create(name="Test Org")
        self.assertEqual(str(org), "Test Org")
    
    def test_multiple_organizations(self):
        org1 = models.Organization.objects.create(name="Org 1")
        org2 = models.Organization.objects.create(name="Org 2")
        self.assertEqual(models.Organization.objects.count(), 2)
        self.assertNotEqual(org1.id, org2.id)


class UserModelTests(TestCase):
    def setUp(self):
        self.org = models.Organization.objects.create(name="Test Org")
    
    def test_create_user(self):
        user = User.objects.create_user(
            username="testuser",
            password="testpass123",
            organization=self.org
        )
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.organization, self.org)
    
    def test_user_password_hashing(self):
        user = User.objects.create_user(
            username="testuser",
            password="testpass123",
            organization=self.org
        )
        self.assertNotEqual(user.password, "testpass123")
        self.assertTrue(user.check_password("testpass123"))
    
    def test_user_organization_relationship(self):
        user = User.objects.create_user(
            username="testuser",
            password="testpass123",
            organization=self.org
        )
        self.assertEqual(user.organization.name, "Test Org")
    
    def test_user_organization_cascade_delete(self):
        user = User.objects.create_user(
            username="testuser",
            password="testpass123",
            organization=self.org
        )
        user_id = user.id
        self.org.delete()
        self.assertFalse(User.objects.filter(id=user_id).exists())
    
    def test_create_user_without_organization(self):
        with self.assertRaises(TypeError):
            User.objects.create_user(
                username="testuser",
                password="testpass123"
            )
    
    def test_multiple_users_in_organization(self):
        User.objects.create_user(
            username="user1",
            password="pass123",
            organization=self.org
        )
        User.objects.create_user(
            username="user2",
            password="pass123",
            organization=self.org
        )
        self.assertEqual(self.org.user_set.count(), 2)
    
    def test_user_str(self):
        user = User.objects.create_user(
            username="testuser",
            password="testpass123",
            organization=self.org
        )
        self.assertEqual(str(user), "testuser (Test Org)")


class TaskModelTests(TestCase):
    def setUp(self):
        self.org = models.Organization.objects.create(name="Test Org")
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123",
            organization=self.org
        )
    
    def test_create_task(self):
        deadline = timezone.now() + timedelta(days=7)
        task = models.Task.objects.create(
            title="Test Task",
            description="Test Description",
            completed=False,
            assigned_to=self.user,
            organization=self.org,
            deadline_datetime_with_tz=deadline,
            priority=0
        )
        self.assertEqual(task.title, "Test Task")
        self.assertEqual(task.organization, self.org)
        self.assertEqual(task.assigned_to, self.user)
    
    def test_task_organization_cascade_delete(self):
        deadline = timezone.now() + timedelta(days=7)
        task = models.Task.objects.create(
            title="Test Task",
            description="Test Description",
            completed=False,
            assigned_to=self.user,
            organization=self.org,
            deadline_datetime_with_tz=deadline,
            priority=0
        )
        task_id = task.id
        self.org.delete()
        self.assertFalse(models.Task.objects.filter(id=task_id).exists())
    
    def test_task_assigned_to_set_null(self):
        deadline = timezone.now() + timedelta(days=7)
        task = models.Task.objects.create(
            title="Test Task",
            description="Test Description",
            completed=False,
            assigned_to=self.user,
            organization=self.org,
            deadline_datetime_with_tz=deadline,
            priority=0
        )
        self.user.delete()
        task.refresh_from_db()
        self.assertIsNone(task.assigned_to)
    
    def test_task_str(self):
        deadline = timezone.now() + timedelta(days=7)
        task = models.Task.objects.create(
            title="Test Task",
            description="Test Description",
            completed=False,
            assigned_to=self.user,
            organization=self.org,
            deadline_datetime_with_tz=deadline,
            priority=0
        )
        self.assertEqual(str(task), "Test Task")
    
    def test_multiple_tasks_in_organization(self):
        deadline = timezone.now() + timedelta(days=7)
        models.Task.objects.create(
            title="Task 1",
            description="Description 1",
            completed=False,
            assigned_to=self.user,
            organization=self.org,
            deadline_datetime_with_tz=deadline,
            priority=0
        )
        models.Task.objects.create(
            title="Task 2",
            description="Description 2",
            completed=False,
            assigned_to=self.user,
            organization=self.org,
            deadline_datetime_with_tz=deadline,
            priority=1
        )
        self.assertEqual(self.org.task_set.count(), 2)
