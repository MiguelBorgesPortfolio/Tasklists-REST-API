"""
Tests the application API
"""

import base64
import unittest

from app import app, db


def auth_header(username, password):
    """Returns the authorization header."""
    credentials = f'{username}:{password}'
    b64credentials = base64.b64encode(credentials.encode()).decode('utf-8')
    return {'Authorization': f'Basic {b64credentials}'}


class TestBase(unittest.TestCase):
    """Base for all tests."""

    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()
        self.db = db
        self.db.recreate()

    def tearDown(self):
        pass


class TestUsers(TestBase):
    """Tests for the user endpoints."""

    def setUp(self):
        super().setUp()

    def test_correct_credentials(self):
        """Tests the user with correct credentials."""
        credentials = auth_header('homer', '1234')
        res = self.client.get('/api/user/', headers=credentials)
        self.assertEqual(res.status_code, 200)

    def test_wrong_credentials(self):
        """Tests the user with incorrect credentials."""
        credentials = auth_header('no-user', 'no-password')
        res = self.client.get('/api/user/', headers=credentials)
        self.assertEqual(res.status_code, 403)


class TestProjects(TestBase):
    """Tests for the project endpoints."""

    def setUp(self):
        super().setUp()
        self.credentials = auth_header('homer', '1234')

    def test_create_project(self):
        """Tests creating a new project."""
        data = {
            'title': 'New Project',
            'creation_date': '2024-06-28',
            'last_updated': '2024-06-28'
        }
        res = self.client.post('/api/projects/', json=data, headers=self.credentials)
        self.assertEqual(res.status_code, 201)
        self.assertIn('id', res.json)

    def test_get_project(self):
        """Tests getting a project detail."""
        res = self.client.get('/api/projects/1/', headers=self.credentials)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json['title'], 'Doughnuts')

    def test_get_nonexistent_project(self):
        """Tests getting a nonexistent project."""
        res = self.client.get('/api/projects/999/', headers=self.credentials)
        self.assertEqual(res.status_code, 404)

    def test_create_project_invalid_data(self):
        """Tests creating a project with invalid data."""
        data = {
            'title': '',  # Title is required
            'creation_date': '2024-06-28',
            'last_updated': '2024-06-28'
        }
        res = self.client.post('/api/projects/', json=data, headers=self.credentials)
        self.assertEqual(res.status_code, 400)

    def test_update_project(self):
        """Tests updating a project."""
        data = {
            'title': 'Updated Project',
            'last_updated': '2024-06-29'
        }
        res = self.client.put('/api/projects/1/', json=data, headers=self.credentials)
        self.assertEqual(res.status_code, 200)

    def test_update_nonexistent_project(self):
        """Tests updating a nonexistent project."""
        data = {
            'title': 'Updated Project',
            'last_updated': '2024-06-29'
        }
        res = self.client.put('/api/projects/999/', json=data, headers=self.credentials)
        self.assertEqual(res.status_code, 404)

    def test_delete_project(self):
        """Tests deleting a project."""
        res = self.client.delete('/api/projects/1/', headers=self.credentials)
        self.assertEqual(res.status_code, 200)
        # Verify the project is deleted
        res = self.client.get('/api/projects/1/', headers=self.credentials)
        self.assertEqual(res.status_code, 404)

    def test_delete_project_deletes_tasks(self):
        """Tests deleting a project also deletes its tasks."""
        # Create project and tasks
        data = {
            'title': 'Project with Tasks',
            'creation_date': '2024-06-28',
            'last_updated': '2024-06-28'
        }
        self.client.post('/api/projects/', json=data, headers=self.credentials)

        task_data = {
            'title': 'Task 1',
            'creation_date': '2024-06-28',
            'completed': 0
        }
        self.client.post('/api/projects/1/tasks/', json=task_data, headers=self.credentials)

        task_data = {
            'title': 'Task 2',
            'creation_date': '2024-06-28',
            'completed': 0
        }
        self.client.post('/api/projects/1/tasks/', json=task_data, headers=self.credentials)

        # Delete project
        res = self.client.delete('/api/projects/1/', headers=self.credentials)
        self.assertEqual(res.status_code, 200)

        # Verify the tasks are deleted
        res = self.client.get('/api/projects/1/tasks/1/', headers=self.credentials)
        self.assertEqual(res.status_code, 404)
        res = self.client.get('/api/projects/1/tasks/2/', headers=self.credentials)
        self.assertEqual(res.status_code, 404)

    def test_access_nonexistent_project_tasks(self):
        """Tests accessing tasks of a nonexistent project."""
        res = self.client.get('/api/projects/999/tasks/', headers=self.credentials)
        self.assertEqual(res.status_code, 404)


class TestTasks(TestBase):
    """Tests for the tasks endpoints."""

    def setUp(self):
        super().setUp()
        self.credentials = auth_header('homer', '1234')

    def test_create_task(self):
        """Tests creating a new task."""
        data = {
            'title': 'New Task',
            'creation_date': '2024-06-28',
            'completed': 0
        }
        res = self.client.post('/api/projects/1/tasks/', json=data, headers=self.credentials)
        self.assertEqual(res.status_code, 201)
        self.assertIn('id', res.json)

    def test_create_task_invalid_data(self):
        """Tests creating a task with invalid data."""
        data = {
            'title': '',  # Title is required
            'creation_date': '2024-06-28',
            'completed': 0
        }
        res = self.client.post('/api/projects/1/tasks/', json=data, headers=self.credentials)
        self.assertEqual(res.status_code, 400)

    def test_get_task(self):
        """Tests getting a task detail."""
        res = self.client.get('/api/projects/1/tasks/1/', headers=self.credentials)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json['title'], 'Search for doughnuts')

    def test_get_nonexistent_task(self):
        """Tests getting a nonexistent task."""
        res = self.client.get('/api/projects/1/tasks/999/', headers=self.credentials)
        self.assertEqual(res.status_code, 404)

    def test_update_task(self):
        """Tests updating a task."""
        data = {
            'title': 'Updated Task',
            'completed': 1
        }
        res = self.client.put('/api/projects/1/tasks/1/', json=data, headers=self.credentials)
        self.assertEqual(res.status_code, 200)

    def test_update_nonexistent_task(self):
        """Tests updating a nonexistent task."""
        data = {
            'title': 'Updated Task',
            'completed': 1
        }
        res = self.client.put('/api/projects/1/tasks/999/', json=data, headers=self.credentials)
        self.assertEqual(res.status_code, 404)

    def test_delete_task(self):
        """Tests deleting a task."""
        res = self.client.delete('/api/projects/1/tasks/1/', headers=self.credentials)
        self.assertEqual(res.status_code, 200)
        # Verify the task is deleted
        res = self.client.get('/api/projects/1/tasks/1/', headers=self.credentials)
        self.assertEqual(res.status_code, 404)

    def test_access_nonexistent_project_tasks(self):
        """Tests accessing tasks of a nonexistent project."""
        res = self.client.get('/api/projects/999/tasks/', headers=self.credentials)
        self.assertEqual(res.status_code, 404)


class TestMessages(TestBase):
    """Tests for the messages endpoints."""

    def setUp(self):
        super().setUp()
        self.credentials = auth_header('homer', '1234')
        self.receiver_credentials = auth_header('bart', '1234')

    def test_send_message(self):
        """Tests sending a message."""
        data = {
            'receiver_id': 2,
            'content': 'Hello, Bart!'
        }
        res = self.client.post('/api/messages/', json=data, headers=self.credentials)
        self.assertEqual(res.status_code, 201)
        self.assertIn('id', res.json)

    def test_send_message_invalid_data(self):
        """Tests sending a message with invalid data."""
        data = {
            'receiver_id': 2,
            'content': ''
        }
        res = self.client.post('/api/messages/', json=data, headers=self.credentials)
        self.assertEqual(res.status_code, 400)

    def test_list_messages(self):
        """Tests listing messages."""
        res = self.client.get('/api/messages/', headers=self.receiver_credentials)
        self.assertEqual(res.status_code, 200)
        self.assertIsInstance(res.json, list)


    def test_delete_nonexistent_message(self):
        """Tests deleting a nonexistent message."""
        res = self.client.delete('/api/messages/999/', headers=self.credentials)
        self.assertEqual(res.status_code, 404)


class TestTaskCompleted(TestBase):
    """Tests for updating task completed status."""

    def setUp(self):
        super().setUp()
        self.credentials = auth_header('homer', '1234')

    def test_update_task_completed_status(self):
        """Tests updating a task's completed status."""
        data = {
            'completed': 1
        }
        res = self.client.patch('/api/tasks/1/completed/', json=data, headers=self.credentials)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json['completed'], 1)

    def test_update_nonexistent_task_completed_status(self):
        """Tests updating a nonexistent task's completed status."""
        data = {
            'completed': 1
        }
        res = self.client.patch('/api/tasks/999/completed/', json=data, headers=self.credentials)
        self.assertEqual(res.status_code, 404)


if __name__ == '__main__':
    unittest.main()
