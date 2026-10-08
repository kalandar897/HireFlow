from django.test import TestCase, Client
from django.urls import reverse
from jobs.models import Job
from applications.models import Application
from accounts.models import User
from interviews.models import Interview
from django.utils import timezone
from datetime import timedelta

class RoleAccessTests(TestCase):

    def setUp(self):
        self.client = Client()

        self.candidate = User.objects.create_user(
            username="testcandidate",
            email="candidate@test.com",
            password="TestPass123",
            role="CANDIDATE",
        )

        self.recruiter = User.objects.create_user(
            username="testrecruiter",
            email="recruiter@test.com",
            password="TestPass123",
            role="RECRUITER",
        )

    def test_candidate_cannot_access_recruiter_dashboard(self):
        self.client.login(
            username="testcandidate",
            password="TestPass123"
        )

        response = self.client.get(
            reverse("recruiter_dashboard")
        )

        self.assertEqual(response.status_code, 403)

    def test_recruiter_cannot_access_candidate_dashboard(self):
        self.client.login(
            username="testrecruiter",
            password="TestPass123"
        )

        response = self.client.get(
            reverse("candidate_dashboard")
        )

        self.assertEqual(response.status_code, 403)

    def test_recruiter_cannot_edit_another_recruiters_job(self):
        job = Job.objects.create(
            recruiter=self.recruiter,
            title="Python Developer",
            company="Test Company",
            description="Test job",
            location="Bengaluru",
            required_skills="Python, Django",
        )

        another_recruiter = User.objects.create_user(
            username="anotherrecruiter",
            email="another@test.com",
            password="TestPass123",
            role="RECRUITER",
        )

        self.client.login(
            username="anotherrecruiter",
            password="TestPass123"
        )

        response = self.client.get(
            reverse("edit_job", args=[job.id])
        )

        self.assertEqual(response.status_code, 404)

    def test_recruiter_cannot_update_another_recruiters_application(self):
        job = Job.objects.create(
            recruiter=self.recruiter,
            title="Python Developer",
            company="Test Company",
            description="Test job",
            location="Bengaluru",
            required_skills="Python, Django",
        )

        application = Application.objects.create(
            candidate=self.candidate,
            job=job,
            status="APPLIED",
        )

        another_recruiter = User.objects.create_user(
            username="anotherrecruiter2",
            email="another2@test.com",
            password="TestPass123",
            role="RECRUITER",
        )

        self.client.login(
            username="anotherrecruiter2",
            password="TestPass123"
        )

        response = self.client.post(
            reverse(
                "update_application_status",
                args=[application.id]
            ),
            {"status": "SELECTED"},
        )

        self.assertEqual(response.status_code, 404)

    def test_recruiter_cannot_update_another_recruiters_interview(self):

        job = Job.objects.create(
            recruiter=self.recruiter,
            title="Python Developer",
            company="Test Company",
            description="Test job",
            location="Bengaluru",
            required_skills="Python, Django",
        )

        application = Application.objects.create(
            candidate=self.candidate,
            job=job,
            status="SHORTLISTED",
        )

        interview = Interview.objects.create(
            application=application,
            interview_date=timezone.now() + timedelta(days=1),
            meeting_mode="ONLINE",
            status="SCHEDULED",
        )

        another_recruiter = User.objects.create_user(
            username="anotherrecruiter3",
            email="another3@test.com",
            password="TestPass123",
            role="RECRUITER",
        )

        self.client.login(
            username="anotherrecruiter3",
            password="TestPass123"
        )

        response = self.client.post(
            reverse(
                "update_interview_status",
                args=[interview.id]
            ),
            {"status": "COMPLETED"},
        )

        self.assertEqual(response.status_code, 404)

    def test_unauthenticated_user_cannot_access_candidate_dashboard(self):
        response = self.client.get(
            reverse("candidate_dashboard")
        )

        self.assertEqual(response.status_code, 302)


    def test_unauthenticated_user_cannot_access_recruiter_dashboard(self):
        response = self.client.get(
            reverse("recruiter_dashboard")
        )

        self.assertEqual(response.status_code, 302)

    def test_candidate_cannot_access_admin_dashboard(self):
        self.client.login(
            username="testcandidate",
            password="TestPass123"
        )

        response = self.client.get(
            reverse("admin_dashboard")
        )

        self.assertEqual(response.status_code, 403)