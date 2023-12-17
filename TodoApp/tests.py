from django.test import TestCase, Client
from rest_framework import status
from rest_framework.test import APIClient
from django.urls import reverse
from .serializers import TaskSerializer
from datetime import datetime, timedelta
from .models import Task
import base64
from django.contrib.auth.models import User

class TaskModelTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        username = 'manoj'
        password = '123'
        credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
        self.client.credentials(HTTP_AUTHORIZATION=f"Basic {credentials}")

        self.sample_task = Task.objects.create(
            title='Sample Task',
            description='Test description',
            due_date=datetime.now().date() + timedelta(days=3),
            tags='tag1, tag2',
            status='OPEN'
        )

    def test_task_creation(self):
        self.assertEqual(self.sample_task.title, 'Sample Task')
        self.assertEqual(self.sample_task.status, 'OPEN')
        self.assertLessEqual(len(self.sample_task.title), 100)
        self.assertLessEqual(len(self.sample_task.description), 1000)

    def test_auto_timestamp(self):
        self.assertIsNotNone(self.sample_task.timestamp)
        
    def test_title_max_length(self):
        max_length = self.sample_task._meta.get_field('title').max_length
        self.assertLessEqual(len(self.sample_task.title), max_length)
        
    def test_description_max_length(self):
        max_length = self.sample_task._meta.get_field('description').max_length
        self.assertLessEqual(len(self.sample_task.description), max_length)
    
    def test_due_date_optional(self):
        task_without_due_date = Task.objects.create(
            title='Task without Due Date',
            description='No due date',
            tags='tag3',
            status='OPEN'
        )
        self.assertIsNone(task_without_due_date.due_date)
    
    def test_tag_optional(self):
        task_without_tag = Task.objects.create(
            title='Task without tag',
            description='No tags',
            status='OPEN'
        )
        self.assertIsNone(task_without_tag.tags)

    def test_tags_unique(self):
        task = Task.objects.create(
            title='Task with Duplicate Tags',
            description='Duplicate tags',
            tags='tag1, tag1, tag2, tag2, tag3',
            status='OPEN'
        )
        task_from_db = Task.objects.get(task_id=task.task_id)
        expected_tags = set(['tag1', 'tag2', 'tag3'])
        actual_tags = set(task_from_db.tags.split(', ')) if task_from_db.tags else set()
        self.assertEqual(actual_tags, expected_tags)

    def test_status_choices(self):
        valid_status_choices = ['OPEN', 'WORKING', 'DONE', 'OVERDUE']
        task_status_choices = [choice[0] for choice in Task.STATUS_CHOICES]
        self.assertListEqual(task_status_choices, valid_status_choices)

class TaskViewsTestCase(TestCase):
    def setUp(self):
        
        self.client = APIClient()
        self.username = 'manoj'
        self.password = '123'
        self.user = User.objects.create_user(username=self.username, password=self.password)
        success = self.client.login(username=self.username, password=self.password)
        
        self.task1 = Task.objects.create(
            title='Task 1',
            description='Description for Task 1',
            due_date='2023-12-31',
            tags='tag1, tag2',
            status='OPEN'
        )
        self.task2 = Task.objects.create(
            title='Task 2',
            description='Description for Task 2',
            due_date='2023-12-25',
            tags='tag3',
            status='WORKING'
        )

    def test_task_list_endpoint(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Basic {base64.b64encode(f"{self.username}:{self.password}".encode()).decode()}')
        response = self.client.get(reverse('task-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        tasks = Task.objects.all()
        serializer = TaskSerializer(tasks, many=True)
        self.assertEqual(response.data, serializer.data)

    def test_create_task_endpoint(self):
        new_task_data = {
            "title": "New Task",
            "description": "Description for New Task",
            "due_date": "2024-01-15",
            "tags": "tag4, tag5",
            "status": "OPEN"
        }
        self.client.credentials(HTTP_AUTHORIZATION=f'Basic {base64.b64encode(f"{self.username}:{self.password}".encode()).decode()}')
        response = self.client.post(reverse('task-list'), new_task_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        new_task = Task.objects.get(title="New Task")
        self.assertEqual(new_task.description, "Description for New Task")

    def test_update_task_endpoint(self):
        update_data = {
            "title": "Updated Task Title",
            "description": "Updated Description",
            "due_date": "2024-01-20",
            "tags": "tag6",
            "status": "DONE"
        }
        self.client.credentials(HTTP_AUTHORIZATION=f'Basic {base64.b64encode(f"{self.username}:{self.password}".encode()).decode()}')
        response = self.client.put(reverse('task-detail', args=[self.task1.pk]), update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_task = Task.objects.get(pk=self.task1.pk)
        self.assertEqual(updated_task.title, "Updated Task Title")

    def test_delete_task_endpoint(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Basic {base64.b64encode(f"{self.username}:{self.password}".encode()).decode()}')
        response = self.client.delete(reverse('task-detail', args=[self.task2.pk]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Task.objects.filter(pk=self.task2.pk).exists())
