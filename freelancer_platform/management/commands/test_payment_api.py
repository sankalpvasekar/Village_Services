from django.core.management.base import BaseCommand
from django.test import Client
from django.contrib.auth.models import User
from freelancer_platform.models import UserProfile, Job, JobRequest, Payment
from decimal import Decimal
import json

class Command(BaseCommand):
    help = 'Test payment API endpoints'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🌐 Testing Payment API Endpoints...'))
        
        # Create test client
        self.client = Client()
        
        # Test payment endpoints
        self.test_payment_endpoints()
        
        self.stdout.write(self.style.SUCCESS('\n✅ Payment API Testing Completed!'))

    def test_payment_endpoints(self):
        """Test payment-related API endpoints"""
        self.stdout.write('\n📡 Testing API Endpoints...')
        
        # Test payment history endpoint
        self.test_payment_history_endpoint()
        
        # Test payment test endpoint
        self.test_payment_test_endpoint()
        
        # Test dashboard endpoints
        self.test_dashboard_endpoints()

    def test_payment_history_endpoint(self):
        """Test payment history endpoint"""
        self.stdout.write('  📊 Testing Payment History Endpoint...')
        
        # Create test user and login
        user = User.objects.create_user(
            username='api_test_user',
            email='api@test.com',
            password='testpass123'
        )
        
        UserProfile.objects.create(
            user=user,
            user_type='freelancer',
            phone='1234567890'
        )
        
        # Login
        self.client.force_login(user)
        
        # Test payment history page
        response = self.client.get('/payment-history/')
        
        if response.status_code == 200:
            self.stdout.write('    ✓ Payment history endpoint working')
        else:
            self.stdout.write(f'    ❌ Payment history endpoint failed: {response.status_code}')

    def test_payment_test_endpoint(self):
        """Test payment test endpoint"""
        self.stdout.write('  🧪 Testing Payment Test Endpoint...')
        
        # Test payment test page
        response = self.client.get('/payment-test/')
        
        if response.status_code == 200:
            self.stdout.write('    ✓ Payment test endpoint working')
        else:
            self.stdout.write(f'    ❌ Payment test endpoint failed: {response.status_code}')

    def test_dashboard_endpoints(self):
        """Test dashboard endpoints"""
        self.stdout.write('  🏠 Testing Dashboard Endpoints...')
        
        # Test freelancer dashboard
        response = self.client.get('/dashboard/')
        
        if response.status_code == 200:
            self.stdout.write('    ✓ Dashboard endpoint working')
        else:
            self.stdout.write(f'    ❌ Dashboard endpoint failed: {response.status_code}')

    def test_payment_creation_api(self):
        """Test payment creation via API"""
        self.stdout.write('  💳 Testing Payment Creation API...')
        
        # This would test actual payment creation
        # For now, just test the endpoint exists
        response = self.client.get('/payment-test/')
        
        if response.status_code == 200:
            self.stdout.write('    ✓ Payment creation API accessible')
        else:
            self.stdout.write(f'    ❌ Payment creation API failed: {response.status_code}')
