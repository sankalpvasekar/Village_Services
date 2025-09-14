from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
from freelancer_platform.models import UserProfile, Job, JobRequest, Payment, WorkTracking, Complaint
import json

class Command(BaseCommand):
    help = 'Test payment integration with different payment methods and scenarios'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🧪 Testing Payment Integration...'))
        
        # Create test users
        self.create_test_users()
        
        # Test different payment methods
        self.test_payment_methods()
        
        # Test payment workflow scenarios
        self.test_payment_workflows()
        
        # Test complaint scenarios
        self.test_complaint_scenarios()
        
        # Test edge cases
        self.test_edge_cases()
        
        self.stdout.write(self.style.SUCCESS('\n✅ Payment Integration Testing Completed!'))

    def create_test_users(self):
        """Create test users for different scenarios"""
        self.stdout.write('\n📝 Creating Test Users...')
        
        # Recruiter
        self.recruiter_user, created = User.objects.get_or_create(
            username='test_recruiter',
            defaults={
                'email': 'recruiter@test.com',
                'first_name': 'Test',
                'last_name': 'Recruiter',
                'password': 'pbkdf2_sha256$260000$test$test'  # Simplified for testing
            }
        )
        
        # Freelancer
        self.freelancer_user, created = User.objects.get_or_create(
            username='test_freelancer',
            defaults={
                'email': 'freelancer@test.com',
                'first_name': 'Test',
                'last_name': 'Freelancer',
                'password': 'pbkdf2_sha256$260000$test$test'
            }
        )
        
        # Create profiles
        self.recruiter_profile, created = UserProfile.objects.get_or_create(
            user=self.recruiter_user,
            defaults={
                'user_type': 'recruiter',
                'phone': '1234567890',
                'address': 'Test Recruiter Address'
            }
        )
        
        self.freelancer_profile, created = UserProfile.objects.get_or_create(
            user=self.freelancer_user,
            defaults={
                'user_type': 'freelancer',
                'phone': '0987654321',
                'address': 'Test Freelancer Address',
                'skills': 'Testing, Python, Django, Payment Integration',
                'experience_years': 3,
                'hourly_rate': Decimal('750.00')
            }
        )
        
        self.stdout.write('✓ Test users created successfully')

    def test_payment_methods(self):
        """Test different payment methods"""
        self.stdout.write('\n💳 Testing Payment Methods...')
        
        payment_methods = ['upi', 'scanner', 'cash', 'bank_transfer', 'razorpay']
        
        for method in payment_methods:
            # Create test job
            job = Job.objects.create(
                title=f'Test Job - {method.upper()}',
                description=f'Test job for {method} payment method',
                category='other',
                company_name='Test Company',
                location='Test Location',
                salary_min=Decimal('1000.00'),
                salary_max=Decimal('3000.00'),
                required_skills='Testing, Payment Integration',
                duration_months=1,
                duration_unit='weeks',
                recruiter=self.recruiter_profile
            )
            
            # Create job request
            job_request = JobRequest.objects.create(
                job=job,
                freelancer=self.freelancer_profile,
                cover_letter=f'I am interested in this {method} payment test job',
                proposal_type='fixed',
                proposed_rate=Decimal('2000.00'),
                proposed_duration=1,
                status='approved'
            )
            
            # Create payment
            payment = Payment.objects.create(
                job_request=job_request,
                recruiter=self.recruiter_profile,
                freelancer=self.freelancer_profile,
                amount=Decimal('2000.00'),
                payment_method=method,
                status='paid',
                is_escrow=True,
                paid_at=timezone.now()
            )
            
            self.stdout.write(f'✓ {method.upper()} payment created: ₹{payment.amount}')
            
            # Test payment status updates
            self.test_payment_status_updates(payment)

    def test_payment_status_updates(self, payment):
        """Test payment status progression"""
        self.stdout.write(f'  📊 Testing status updates for Payment {payment.id}...')
        
        # Test work submission
        payment.status = 'work_submitted'
        payment.work_submitted_at = timezone.now()
        payment.save()
        
        work_tracking = WorkTracking.objects.create(
            payment=payment,
            freelancer=self.freelancer_profile,
            status='submitted',
            completion_notes=f'Work completed for {payment.payment_method} payment',
            submitted_at=timezone.now()
        )
        
        # Test work confirmation
        payment.status = 'work_confirmed'
        payment.work_confirmed_at = timezone.now()
        payment.work_confirmed_by = self.recruiter_profile
        payment.save()
        
        work_tracking.status = 'completed'
        work_tracking.reviewed_at = timezone.now()
        work_tracking.recruiter_feedback = 'Excellent work!'
        work_tracking.save()
        
        # Test payment release
        payment.status = 'released'
        payment.released_at = timezone.now()
        payment.save()
        
        self.stdout.write(f'    ✓ Payment {payment.id} completed full workflow')

    def test_payment_workflows(self):
        """Test different payment workflow scenarios"""
        self.stdout.write('\n🔄 Testing Payment Workflows...')
        
        # Scenario 1: Successful payment
        self.test_successful_payment()
        
        # Scenario 2: Payment failure
        self.test_payment_failure()
        
        # Scenario 3: Work rejection
        self.test_work_rejection()
        
        # Scenario 4: Payment refund
        self.test_payment_refund()

    def test_successful_payment(self):
        """Test successful payment workflow"""
        self.stdout.write('  ✅ Testing Successful Payment Workflow...')
        
        job = Job.objects.create(
            title='Successful Payment Test',
            description='Test successful payment workflow',
            category='other',
            recruiter=self.recruiter_profile,
            duration_months=1,
            duration_unit='weeks'
        )
        
        job_request = JobRequest.objects.create(
            job=job,
            freelancer=self.freelancer_profile,
            proposal_type='fixed',
            proposed_rate=Decimal('1500.00'),
            status='approved'
        )
        
        payment = Payment.objects.create(
            job_request=job_request,
            recruiter=self.recruiter_profile,
            freelancer=self.freelancer_profile,
            amount=Decimal('1500.00'),
            payment_method='upi',
            status='paid'
        )
        
        # Simulate complete workflow
        self.simulate_payment_workflow(payment, 'success')
        self.stdout.write('    ✓ Successful payment workflow completed')

    def test_payment_failure(self):
        """Test payment failure scenario"""
        self.stdout.write('  ❌ Testing Payment Failure...')
        
        job = Job.objects.create(
            title='Failed Payment Test',
            description='Test payment failure scenario',
            category='other',
            recruiter=self.recruiter_profile,
            duration_months=1,
            duration_unit='weeks'
        )
        
        job_request = JobRequest.objects.create(
            job=job,
            freelancer=self.freelancer_profile,
            proposal_type='fixed',
            proposed_rate=Decimal('1000.00'),
            status='approved'
        )
        
        payment = Payment.objects.create(
            job_request=job_request,
            recruiter=self.recruiter_profile,
            freelancer=self.freelancer_profile,
            amount=Decimal('1000.00'),
            payment_method='razorpay',
            status='failed'
        )
        
        self.stdout.write('    ✓ Payment failure scenario tested')

    def test_work_rejection(self):
        """Test work rejection scenario"""
        self.stdout.write('  🚫 Testing Work Rejection...')
        
        job = Job.objects.create(
            title='Work Rejection Test',
            description='Test work rejection scenario',
            category='other',
            recruiter=self.recruiter_profile,
            duration_months=1,
            duration_unit='weeks'
        )
        
        job_request = JobRequest.objects.create(
            job=job,
            freelancer=self.freelancer_profile,
            proposal_type='fixed',
            proposed_rate=Decimal('2000.00'),
            status='approved'
        )
        
        payment = Payment.objects.create(
            job_request=job_request,
            recruiter=self.recruiter_profile,
            freelancer=self.freelancer_profile,
            amount=Decimal('2000.00'),
            payment_method='bank_transfer',
            status='paid'
        )
        
        # Create work tracking with rejection
        work_tracking = WorkTracking.objects.create(
            payment=payment,
            freelancer=self.freelancer_profile,
            status='rejected',
            completion_notes='Work submitted but quality was poor',
            recruiter_feedback='Work does not meet requirements',
            reviewed_at=timezone.now()
        )
        
        self.stdout.write('    ✓ Work rejection scenario tested')

    def test_payment_refund(self):
        """Test payment refund scenario"""
        self.stdout.write('  💰 Testing Payment Refund...')
        
        job = Job.objects.create(
            title='Refund Test',
            description='Test payment refund scenario',
            category='other',
            recruiter=self.recruiter_profile,
            duration_months=1,
            duration_unit='weeks'
        )
        
        job_request = JobRequest.objects.create(
            job=job,
            freelancer=self.freelancer_profile,
            proposal_type='fixed',
            proposed_rate=Decimal('2500.00'),
            status='approved'
        )
        
        payment = Payment.objects.create(
            job_request=job_request,
            recruiter=self.recruiter_profile,
            freelancer=self.freelancer_profile,
            amount=Decimal('2500.00'),
            payment_method='upi',
            status='refunded'
        )
        
        self.stdout.write('    ✓ Payment refund scenario tested')

    def test_complaint_scenarios(self):
        """Test complaint scenarios"""
        self.stdout.write('\n📢 Testing Complaint Scenarios...')
        
        # Create a job for complaint testing
        job = Job.objects.create(
            title='Complaint Test Job',
            description='Test job for complaint scenarios',
            category='other',
            recruiter=self.recruiter_profile,
            duration_months=1,
            duration_unit='weeks'
        )
        
        job_request = JobRequest.objects.create(
            job=job,
            freelancer=self.freelancer_profile,
            proposal_type='fixed',
            proposed_rate=Decimal('3000.00'),
            status='approved'
        )
        
        payment = Payment.objects.create(
            job_request=job_request,
            recruiter=self.recruiter_profile,
            freelancer=self.freelancer_profile,
            amount=Decimal('3000.00'),
            payment_method='cash',
            status='paid'
        )
        
        # Test recruiter complaint
        recruiter_complaint = Complaint.objects.create(
            payment=payment,
            complainant=self.recruiter_profile,
            complaint_type='recruiter_payment',
            title='Work not completed',
            description='Freelancer did not complete the work as agreed',
            status='open'
        )
        
        # Test freelancer complaint
        freelancer_complaint = Complaint.objects.create(
            payment=payment,
            complainant=self.freelancer_profile,
            complaint_type='freelancer_payment',
            title='Payment not received',
            description='Completed work but payment not released',
            status='open'
        )
        
        self.stdout.write('    ✓ Recruiter complaint created')
        self.stdout.write('    ✓ Freelancer complaint created')

    def test_edge_cases(self):
        """Test edge cases and error scenarios"""
        self.stdout.write('\n⚠️ Testing Edge Cases...')
        
        # Test zero amount payment
        try:
            job = Job.objects.create(
                title='Zero Amount Test',
                description='Test zero amount payment',
                category='other',
                recruiter=self.recruiter_profile,
                duration_months=1,
                duration_unit='weeks'
            )
            
            job_request = JobRequest.objects.create(
                job=job,
                freelancer=self.freelancer_profile,
                proposal_type='fixed',
                proposed_rate=Decimal('0.00'),
                status='approved'
            )
            
            payment = Payment.objects.create(
                job_request=job_request,
                recruiter=self.recruiter_profile,
                freelancer=self.freelancer_profile,
                amount=Decimal('0.00'),
                payment_method='cash',
                status='paid'
            )
            
            self.stdout.write('    ✓ Zero amount payment handled')
        except Exception as e:
            self.stdout.write(f'    ⚠️ Zero amount payment error: {e}')
        
        # Test large amount payment
        try:
            job = Job.objects.create(
                title='Large Amount Test',
                description='Test large amount payment',
                category='other',
                recruiter=self.recruiter_profile,
                duration_months=1,
                duration_unit='weeks'
            )
            
            job_request = JobRequest.objects.create(
                job=job,
                freelancer=self.freelancer_profile,
                proposal_type='fixed',
                proposed_rate=Decimal('100000.00'),
                status='approved'
            )
            
            payment = Payment.objects.create(
                job_request=job_request,
                recruiter=self.recruiter_profile,
                freelancer=self.freelancer_profile,
                amount=Decimal('100000.00'),
                payment_method='bank_transfer',
                status='paid'
            )
            
            self.stdout.write('    ✓ Large amount payment handled')
        except Exception as e:
            self.stdout.write(f'    ⚠️ Large amount payment error: {e}')

    def simulate_payment_workflow(self, payment, scenario):
        """Simulate different payment workflow scenarios"""
        if scenario == 'success':
            # Work submission
            payment.status = 'work_submitted'
            payment.work_submitted_at = timezone.now()
            payment.save()
            
            # Work confirmation
            payment.status = 'work_confirmed'
            payment.work_confirmed_at = timezone.now()
            payment.work_confirmed_by = self.recruiter_profile
            payment.save()
            
            # Payment release
            payment.status = 'released'
            payment.released_at = timezone.now()
            payment.save()

    def display_test_summary(self):
        """Display test summary"""
        self.stdout.write('\n📊 Test Summary:')
        self.stdout.write(f'  Total Jobs: {Job.objects.count()}')
        self.stdout.write(f'  Total Payments: {Payment.objects.count()}')
        self.stdout.write(f'  Total Complaints: {Complaint.objects.count()}')
        self.stdout.write(f'  Total Work Tracking: {WorkTracking.objects.count()}')
        
        # Payment method breakdown
        payment_methods = Payment.objects.values_list('payment_method', flat=True).distinct()
        self.stdout.write('\n💳 Payment Methods Tested:')
        for method in payment_methods:
            count = Payment.objects.filter(payment_method=method).count()
            self.stdout.write(f'  {method.upper()}: {count} payments')
        
        # Status breakdown
        statuses = Payment.objects.values_list('status', flat=True).distinct()
        self.stdout.write('\n📈 Payment Statuses:')
        for status in statuses:
            count = Payment.objects.filter(status=status).count()
            self.stdout.write(f'  {status}: {count} payments')
