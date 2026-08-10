# profiles/tests/test_video_progress.py
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth.models import User
from profiles.models import Profile, VideoProgress
from courses.models import Course, Lesson
import json

# SECURE_SSL_REDIRECT is True whenever DEBUG=False (the site's real .env has
# DEBUG=False), which was 301-redirecting every request the test client made
# before it ever reached the view - every assertion here was failing for a
# reason unrelated to the code under test. Disable it for these tests.
@override_settings(SECURE_SSL_REDIRECT=False)
class VideoProgressTestCase(TestCase):
    def setUp(self):
        # Create test user
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.profile = Profile.objects.get(user=self.user)
        
        # Create test course and lesson
        self.course = Course.objects.create(
            title='Test Course',
            slug='test-course',
            status='publish'
        )
        
        self.lesson = Lesson.objects.create(
            course=self.course,
            title='Test Lesson',
            slug='test-lesson',
            status='publish',
            youtube_url='https://www.youtube.com/watch?v=test123'
        )

    def test_ajax_required(self):
        """Test that non-AJAX requests are rejected"""
        self.client.force_login(self.user)
        response = self.client.post(
            reverse('profiles:mark_video_watched', args=[self.lesson.id]),
            data={'current_time': 120}
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(json.loads(response.content)['message'], 'AJAX requests required')

    def test_mark_video_watched_authenticated(self):
        """Test video progress tracking for authenticated user"""
        self.client.force_login(self.user)
        
        # Test data
        progress_data = {
            'current_time': 120,
            'is_completed': False
        }
        
        # Make request
        response = self.client.post(
            reverse('profiles:mark_video_watched', args=[self.lesson.id]),
            data=json.dumps(progress_data),
            content_type='application/json',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        # Check response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'success')
        
        # Verify database record
        progress = VideoProgress.objects.get(user=self.user, lesson=self.lesson)
        self.assertEqual(progress.current_time, 120)
        self.assertFalse(progress.is_completed)

    def test_mark_video_completed(self):
        """Test marking video as completed"""
        self.client.force_login(self.user)
        
        progress_data = {
            'current_time': 300,
            'is_completed': True
        }
        
        response = self.client.post(
            reverse('profiles:mark_video_watched', args=[self.lesson.id]),
            data=json.dumps(progress_data),
            content_type='application/json',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Verify completion status
        progress = VideoProgress.objects.get(user=self.user, lesson=self.lesson)
        self.assertTrue(progress.is_completed)
        self.assertIn(self.lesson, self.user.profile.watched_videos.all())

    def test_get_video_progress(self):
        """Test retrieving saved video progress"""
        self.client.force_login(self.user)
        
        # Create initial progress
        VideoProgress.objects.create(
            user=self.user,
            lesson=self.lesson,
            current_time=150,
            is_completed=False
        )
        
        response = self.client.get(
            reverse('profiles:get_video_progress', args=[self.lesson.id])
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['current_time'], 150)
        self.assertFalse(data['is_completed'])

    def test_invalid_lesson_id(self):
        """Test handling of invalid lesson ID"""
        self.client.force_login(self.user)
        
        response = self.client.post(
            reverse('profiles:mark_video_watched', args=[99999]),
            data=json.dumps({'current_time': 100}),
            content_type='application/json',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        self.assertEqual(response.status_code, 404)

    def test_invalid_data_format(self):
        """Test handling of invalid data"""
        self.client.force_login(self.user)
        
        invalid_data = {
            'current_time': 'invalid',
        }
        
        response = self.client.post(
            reverse('profiles:mark_video_watched', args=[self.lesson.id]),
            data=json.dumps(invalid_data),
            content_type='application/json',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        self.assertEqual(response.status_code, 400)

    def test_unauthenticated_access(self):
        """Test access by unauthenticated user"""
        response = self.client.post(
            reverse('profiles:mark_video_watched', args=[self.lesson.id]),
            data=json.dumps({'current_time': 100}),
            content_type='application/json',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_course_progress_calculation(self):
        """Test course progress calculation"""
        self.client.force_login(self.user)
        
        # Create additional lesson
        lesson2 = Lesson.objects.create(
            course=self.course,
            title='Test Lesson 2',
            slug='test-lesson-2',
            status='publish'
        )
        
        # Mark first lesson as complete
        progress_data = {
            'current_time': 300,
            'is_completed': True
        }
        
        response = self.client.post(
            reverse('profiles:mark_video_watched', args=[self.lesson.id]),
            data=json.dumps(progress_data),
            content_type='application/json',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        # Verify course progress
        self.profile.refresh_from_db()
        progress = self.profile.get_course_completion_percentage(self.course)
        self.assertEqual(progress, 50.0)  # 1 out of 2 lessons complete
        