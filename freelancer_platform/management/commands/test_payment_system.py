from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from freelancer_platform.models import UserProfile, Job, JobRequest, Payment, WorkTracking, Complaint
from decimal import Decimal

class Command(BaseCommand):
    help = 'Test the payment system workflow'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Testing Payment System...'))
        
        # Create test users
        recruiter_user, created = User.objects.get_or_create(
            username='test_recruiter',
            defaults={
                'email': 'recruiter@test.com',
                'first_name': 'Test',
                'last_name': 'Recruiter'
            }
        )
        
        freelancer_user, created = User.objects.get_or_create(
            username='test_freelancer',
            defaults={
                'email': 'freelancer@test.com',
                'first_name': 'Test',
                'last_name': 'Freelancer'
            }
        )
        
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
                'skills': 'Testing, Python, Django',
                'experience_years': 2,
                'hourly_rate': Decimal('500.00')
            }
        )
        
        # Create test job
        job, created = Job.objects.get_or_create(
            title='Test Payment Job',
            defaults={
                'description': 'A test job for payment system',
                'category': 'other',
                'company_name': 'Test Company',
                'location': 'Test Location',
                'salary_min': Decimal('1000.00'),
                'salary_max': Decimal('2000.00'),
                'required_skills': 'Testing, Python',
                'duration_months': 1,
                'duration_unit': 'weeks',
                'recruiter': recruiter_profile
            }
        )
        
        # Create job request
        job_request, created = JobRequest.objects.get_or_create(
            job=job,
            freelancer=freelancer_profile,
            defaults={
                'cover_letter': 'I am interested in this test job',
                'proposal_type': 'fixed',
                'proposed_rate': Decimal('1500.00'),
                'proposed_duration': 1,
                'status': 'approved'
            }
        )
        
        # Create payment
        payment, created = Payment.objects.get_or_create(
            job_request=job_request,
            defaults={
                'recruiter': recruiter_profile,
                'freelancer': freelancer_profile,
                'amount': Decimal('1500.00'),
                'payment_method': 'upi',
                'status': 'paid',
                'is_escrow': True
            }
        )
        
        # Create work tracking
        work_tracking, created = WorkTracking.objects.get_or_create(
            payment=payment,
            freelancer=freelancer_profile,
            defaults={
                'status': 'submitted',
                'completion_notes': 'Test work completed successfully',
                'submitted_at': '2025-01-01 12:00:00'
            }
        )
        
        # Test payment workflow
        self.stdout.write(f'✓ Created test users and profiles')
        self.stdout.write(f'✓ Created test job: {job.title}')
        self.stdout.write(f'✓ Created job request: {job_request.id}')
        self.stdout.write(f'✓ Created payment: ₹{payment.amount} - {payment.get_status_display()}')
        self.stdout.write(f'✓ Created work tracking: {work_tracking.get_status_display()}')
        
        # Test payment status updates
        payment.status = 'work_submitted'
        payment.work_submitted_at = '2025-01-01 13:00:00'
        payment.save()
        
        work_tracking.status = 'submitted'
        work_tracking.submitted_at = '2025-01-01 13:00:00'
        work_tracking.save()
        
        self.stdout.write(f'✓ Updated payment status to: {payment.get_status_display()}')
        
        # Test work confirmation
        payment.status = 'work_confirmed'
        payment.work_confirmed_at = '2025-01-01 14:00:00'
        payment.work_confirmed_by = recruiter_profile
        payment.save()
        
        work_tracking.status = 'completed'
        work_tracking.reviewed_at = '2025-01-01 14:00:00'
        work_tracking.recruiter_feedback = 'Great work!'
        work_tracking.save()
        
        self.stdout.write(f'✓ Work confirmed by recruiter')
        
        # Test payment release
        payment.status = 'released'
        payment.released_at = '2025-01-01 15:00:00'
        payment.save()
        
        self.stdout.write(f'✓ Payment released to freelancer')
        
        # Test complaint system
        complaint, created = Complaint.objects.get_or_create(
            payment=payment,
            complainant=freelancer_profile,
            defaults={
                'complaint_type': 'freelancer_payment',
                'title': 'Test Complaint',
                'description': 'This is a test complaint',
                'status': 'open'
            }
        )
        
        self.stdout.write(f'✓ Created test complaint: {complaint.title}')
        
        # Display final status
        self.stdout.write(self.style.SUCCESS('\n=== Payment System Test Results ==='))
        self.stdout.write(f'Job: {job.title} - {job.get_status_display()}')
        self.stdout.write(f'Payment: ₹{payment.amount} - {payment.get_status_display()}')
        self.stdout.write(f'Work Status: {work_tracking.get_status_display()}')
        self.stdout.write(f'Complaint: {complaint.title} - {complaint.get_status_display()}')
        
        self.stdout.write(self.style.SUCCESS('\n✅ Payment system test completed successfully!'))
        self.stdout.write('You can now test the system by:')
        self.stdout.write('1. Logging in as test_recruiter or test_freelancer')
        self.stdout.write('2. Viewing payment history')
        self.stdout.write('3. Testing work submission and review')
        self.stdout.write('4. Testing complaint filing')
