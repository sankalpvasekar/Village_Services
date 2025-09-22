from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from freelancer_platform.models import UserProfile, Job, JobRequest, Payment, WorkTracking

class Command(BaseCommand):
    help = 'Create test data for payment system'

    def handle(self, *args, **options):
        # Create test users if they don't exist
        recruiter_user, created = User.objects.get_or_create(
            username='test_recruiter',
            defaults={
                'email': 'recruiter@test.com',
                'first_name': 'Test',
                'last_name': 'Recruiter'
            }
        )
        if created:
            recruiter_user.set_password('testpass123')
            recruiter_user.save()

        freelancer_user, created = User.objects.get_or_create(
            username='test_freelancer',
            defaults={
                'email': 'freelancer@test.com',
                'first_name': 'Test',
                'last_name': 'Freelancer'
            }
        )
        if created:
            freelancer_user.set_password('testpass123')
            freelancer_user.save()

        # Create user profiles
        recruiter_profile, created = UserProfile.objects.get_or_create(
            user=recruiter_user,
            defaults={
                'user_type': 'recruiter',
                'phone': '1234567890',
                'address': 'Test Address'
            }
        )

        freelancer_profile, created = UserProfile.objects.get_or_create(
            user=freelancer_user,
            defaults={
                'user_type': 'freelancer',
                'phone': '0987654321',
                'address': 'Test Address',
                'experience_years': 2,
                'hourly_rate': 500.00
            }
        )

        # Create a test job
        job, created = Job.objects.get_or_create(
            title='Test Painting Job',
            defaults={
                'description': 'Need someone to paint my house',
                'category': 'painting',
                'company_name': 'Test Company',
                'location': 'Test Location',
                'salary_min': 1000.00,
                'salary_max': 2000.00,
                'required_skills': 'painting, brush work',
                'duration_months': 1,
                'recruiter': recruiter_profile
            }
        )

        # Create a test job request
        job_request, created = JobRequest.objects.get_or_create(
            job=job,
            freelancer=freelancer_profile,
            defaults={
                'cover_letter': 'I am experienced in painting and would love to help with this job.',
                'proposal_type': 'fixed',
                'proposed_rate': 1500.00,
                'proposed_duration': 1,
                'status': 'approved'
            }
        )

        # Create a test payment if it doesn't exist
        if not hasattr(job_request, 'payment'):
            payment = Payment.objects.create(
                job_request=job_request,
                recruiter=recruiter_profile,
                freelancer=freelancer_profile,
                amount=1500.00,
                status='completed'
            )

            # Create work tracking
            WorkTracking.objects.create(
                payment=payment,
                freelancer=freelancer_profile,
                status='completed',
                completion_notes='Painting job completed successfully'
            )

        self.stdout.write(
            self.style.SUCCESS('Test data created successfully!')
        )
        self.stdout.write('Test users:')
        self.stdout.write(f'  Recruiter: {recruiter_user.username} / testpass123')
        self.stdout.write(f'  Freelancer: {freelancer_user.username} / testpass123')
        self.stdout.write(f'  Job ID: {job.id}')
        self.stdout.write(f'  Job Request ID: {job_request.id}')








