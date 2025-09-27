# C:\Users\DDR\OneDrive\Documents\local_freelancer_final\Local_Free_Lancer_New\freelancer_platform\views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db.models import Q, F
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import json
import requests
import os
import re, json as pyjson
from django.utils import timezone
from .models import UserProfile, Job, Application, JobRequest, WorkExample, Payment, WorkTracking, Complaint, LocalResource, Message
from .forms import UserRegistrationForm, JobForm, ApplicationForm, JobRequestForm, FreelancerProfileForm, WorkExampleForm, PaymentForm, WorkTrackingForm, ComplaintForm, AdminComplaintResolutionForm, RecruiterProfileForm, RecruiterUserForm
from .ai_utils import get_skill_recommendations, get_similar_skills, get_job_matching_score
from .api_config import get_api_config, get_skill_config, is_api_enabled


# --- Gemini API and fallback functions ---
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', 'AIzaSyB4Owr1pklmI7WZUE5PqM07HGGZ3drBjRE')

def fetch_gemini_resources(skills, resource_type, api_key=GEMINI_API_KEY):
    prompt = (
        f"Suggest 3-5 high-quality, up-to-date online resources (links/tools/videos) for {resource_type} "
        f"that would help a freelancer with these skills: {', '.join(skills) if skills else 'general skills'}. "
        "For each resource, provide exactly this JSON format: {{\"title\": \"Resource Name\", \"description\": \"Brief description\", \"type\": \"Tool/Video/Article\", \"url\": \"https://example.com\"}}. "
        "Return as a JSON array of these objects."
    )
    try:
        response = requests.post(
            "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent",
            params={"key": api_key},
            json={
                "contents": [{"parts": [{"text": prompt}]}]
            },
            timeout=20
        )
        data = response.json()
        
        if 'candidates' not in data or not data['candidates']:
            print(f"Gemini API error: {data}")
            return []
            
        text = data['candidates'][0]['content']['parts'][0]['text']
        
        # Try to extract JSON from the response
        try:
            match = re.search(r'\[.*\]', text, re.DOTALL)
            if match:
                return pyjson.loads(match.group(0))
            return pyjson.loads(text)
        except pyjson.JSONDecodeError:
            print(f"Failed to parse Gemini response: {text}")
            return get_fallback_resources(resource_type)
            
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        return get_fallback_resources(resource_type)

def get_fallback_resources(resource_type):
    fallback_resources = {
        'financial support and planning': [
            {'title': 'Financial Planning for Freelancers', 'description': 'Comprehensive guide to managing finances as a freelancer', 'type': 'Tool', 'url': 'https://www.mint.com/freelancer-finances'},
            {'title': 'Budget Management App', 'description': 'Free budgeting tool for independent workers', 'type': 'Tool', 'url': 'https://www.youneedabudget.com'}
        ],
        'community support and networking': [
            {'title': 'Local Freelancer Community', 'description': 'Connect with other freelancers in your area', 'type': 'Community', 'url': 'https://www.meetup.com/freelancers'},
            {'title': 'Professional Networking Platform', 'description': 'Build your professional network', 'type': 'Platform', 'url': 'https://www.linkedin.com'}
        ],
        'legal support and worker rights': [
            {'title': 'Freelancer Legal Rights', 'description': 'Information about your rights as a freelancer', 'type': 'Information', 'url': 'https://www.freelancersunion.org/rights'},
            {'title': 'Free Legal Aid Directory', 'description': 'Find free legal assistance in your area', 'type': 'Directory', 'url': 'https://www.lawhelp.org'}
        ],
        'health and wellness support': [
            {'title': 'Healthcare for Freelancers', 'description': 'Health insurance options for independent workers', 'type': 'Information', 'url': 'https://www.healthcare.gov/freelancers'},
            {'title': 'Mental Health Resources', 'description': 'Free mental health support for freelancers', 'type': 'Support', 'url': 'https://www.crisistextline.org'}
        ],
        'emergency assistance and crisis support': [
            {'title': 'Emergency Assistance Hotline', 'description': '24/7 emergency support for freelancers', 'type': 'Hotline', 'url': 'tel:1-800-273-8255'},
            {'title': 'Local Food Bank Directory', 'description': 'Find food assistance in your area', 'type': 'Directory', 'url': 'https://www.feedingamerica.org/find-your-local-foodbank'}
        ]
    }
    return fallback_resources.get(resource_type, [{'title': 'General Resource', 'description': 'Resource for freelancers', 'type': 'Resource', 'url': 'https://www.example.com'}])


def home(request):
    """Home page with login/register options"""
    return render(request, 'freelancer_platform/home.html')

def register(request):
    """User registration with user type selection"""
    user_type = request.GET.get('type', '')
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                user = form.save()
                UserProfile.objects.create(
                    user=user,
                    user_type=form.cleaned_data['user_type'],
                    phone=form.cleaned_data.get('phone', ''),
                    address=form.cleaned_data.get('address', ''),
                )
                login(request, user)
                if form.cleaned_data['user_type'] == 'freelancer':
                    messages.success(request, 'Account created successfully! Welcome to Local Free-Lancer. Start finding job opportunities and building your career.')
                else:
                    messages.success(request, 'Account created successfully! Welcome to Local Free-Lancer. Start posting jobs and connecting with local talent.')
                return redirect('login_redirect')
    else:
        initial_data = {'user_type': user_type} if user_type in ['freelancer', 'recruiter'] else {}
        form = UserRegistrationForm(initial=initial_data)
    return render(request, 'freelancer_platform/register.html', {'form': form, 'user_type': user_type})

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import UserProfile, Job, Application, JobRequest
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def user_login(request):
    """User login with role-based validation."""
    # Corrected line to get 'user_type' from the URL
    user_type_from_url = request.GET.get('user_type', '') 
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            try:
                user_profile = UserProfile.objects.get(user=user)
                # Check if the user's profile type matches the login type
                if user_profile.user_type.lower() == user_type_from_url.lower():
                    login(request, user)
                    if user_profile.user_type == 'freelancer':
                        messages.success(request, f'Welcome back, {user.username}! Ready to find your next opportunity?')
                    else:
                        messages.success(request, f'Welcome back, {user.username}! Ready to connect with local talent?')
                    return redirect('login_redirect')
                else:
                    messages.error(request, 'Access denied. Your credentials do not match this login type.')
            except UserProfile.DoesNotExist:
                messages.error(request, 'User profile not found. Please contact support.')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'freelancer_platform/login.html', {'user_type': user_type_from_url})

@login_required
def user_logout(request):
    """User logout"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')

@login_required
def login_redirect(request):
    """Redirects authenticated users based on their user type."""
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        if user_profile.user_type == 'freelancer':
            return redirect('freelancer_dashboard')
        elif user_profile.user_type == 'recruiter':
            return redirect('recruiter_dashboard')
        else:
            messages.error(request, 'Your account type is not defined. Please contact support.')
            logout(request)
            return redirect('home')
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found. Please log in again.')
        logout(request)
        return redirect('home')

@login_required
def freelancer_dashboard(request):
    """Freelancer dashboard view"""
    user_profile = get_object_or_404(UserProfile, user=request.user)
    if user_profile.user_type != 'freelancer':
        messages.error(request, 'Access denied. You are not a freelancer.')
        return redirect('recruiter_dashboard')
    
    all_available_jobs = Job.objects.filter(status='open').exclude(
        applications__freelancer=user_profile
    ).order_by('-created_at')
    
    page = request.GET.get('page', 1)
    paginator = Paginator(all_available_jobs, 10)
    
    try:
        available_jobs_page = paginator.page(page)
    except PageNotAnInteger:
        available_jobs_page = paginator.page(1)
    except EmptyPage:
        available_jobs_page = paginator.page(paginator.num_pages)
        
    my_applications = Application.objects.filter(freelancer=user_profile)
    my_job_requests = JobRequest.objects.filter(freelancer=user_profile)

    context = {
        'user_profile': user_profile,
        'available_jobs': available_jobs_page,
        'my_applications': my_applications,
        'my_job_requests': my_job_requests,
    }
    return render(request, 'freelancer_platform/freelancer_dashboard.html', context)

@login_required
def recruiter_dashboard(request):
    """Recruiter dashboard view"""
    user_profile = get_object_or_404(UserProfile, user=request.user)
    if user_profile.user_type != 'recruiter':
        messages.error(request, 'Access denied. You are not a recruiter.')
        return redirect('freelancer_dashboard')
    
    posted_jobs = Job.objects.filter(recruiter=user_profile)
    active_jobs = posted_jobs.filter(status='open')
    total_applications = Application.objects.filter(job__recruiter=user_profile)
    job_requests = JobRequest.objects.filter(job__recruiter=user_profile)

    context = {
        'user_profile': user_profile,
        'posted_jobs': posted_jobs,
        'active_jobs': active_jobs,
        'total_applications': total_applications,
        'job_requests': job_requests,
    }
    return render(request, 'freelancer_platform/recruiter_dashboard.html', context)

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def skill_recommendations_api(request):
    """API endpoint for skill-based course recommendations"""
    try:
        data = json.loads(request.body)
        skill_type = data.get('skill_type', 'general')
        user_skills = data.get('user_skills', [])
        api_key = data.get('api_key')
        
        # Get user profile for personalization
        user_profile = UserProfile.objects.get(user=request.user)

        # First: Query local resources prioritized by relevance tags and (optional) location
        tags = [s.lower() for s in user_skills] if user_skills else []
        local_qs = LocalResource.objects.filter(is_active=True)
        if tags:
            local_qs = local_qs.filter(relevance_tags__overlap=tags)
        # Optional: filter by location if profile has address
        if user_profile.address:
            loc = user_profile.address.lower()
            local_qs = local_qs.filter(Q(location__iexact=user_profile.address) | Q(location__icontains=loc))
        local_resources = list(local_qs.values('title','description','resource_type','credibility','url','location')[:20])

        # Fallback: AI/generic recommendations if no local data
        generic = []
        if not local_resources:
            generic = get_skill_recommendations_from_api(skill_type, user_skills, api_key, user_profile)

        return JsonResponse({'success': True, 'local': local_resources, 'generic': generic})
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def certification_links_api(request):
    """API endpoint for certification program links"""
    try:
        data = json.loads(request.body)
        skill_type = data.get('skill_type', 'general')
        user_skills = data.get('user_skills', [])
        api_key = data.get('api_key')
        
        # Get user profile for personalized recommendations
        user_profile = UserProfile.objects.get(user=request.user)
        
        # Mock API response - in production, this would call external APIs
        certifications = get_certification_links_from_api(skill_type, user_skills, api_key, user_profile)
        
        return JsonResponse({
            'success': True,
            'certifications': certifications
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
    
@login_required
@csrf_exempt
@require_http_methods(["POST"])
def online_learning_links_api(request):
    """API endpoint for online learning resources"""
    try:
        data = json.loads(request.body)
        skill_type = data.get('skill_type', 'general')
        user_skills = data.get('user_skills', [])
        api_keys = data.get('api_keys', {})
        
        # Get user profile for personalized recommendations
        user_profile = UserProfile.objects.get(user=request.user)
        
        # Mock API response - in production, this would call external APIs
        resources = get_online_learning_links_from_api(skill_type, user_skills, api_keys, user_profile)
        
        return JsonResponse({
            'success': True,
            'resources': resources
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def financial_resources_api(request):
    try:
        data = json.loads(request.body)
        user_skills = data.get('user_skills', [])
        user_profile = UserProfile.objects.get(user=request.user)
        resources = fetch_gemini_resources(user_skills, 'financial support and planning')
        if not resources:
            resources = [{
                'title': 'General Financial Planning',
                'description': 'Budgeting and financial planning for freelancers.',
                'type': 'Tool',
                'url': 'https://www.example.com/financial-planning',
            }]
        return JsonResponse({'success': True, 'resources': resources})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def community_resources_api(request):
    try:
        data = json.loads(request.body)
        user_skills = data.get('user_skills', [])
        user_profile = UserProfile.objects.get(user=request.user)
        resources = fetch_gemini_resources(user_skills, 'community support and networking')
        if not resources:
            resources = [{
                'title': 'Freelancer Community Forum',
                'description': 'Online forum for all local freelancers.',
                'type': 'Community',
                'url': 'https://www.example.com/freelancer-forum',
            }]
        return JsonResponse({'success': True, 'resources': resources})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def legal_resources_api(request):
    try:
        data = json.loads(request.body)
        user_skills = data.get('user_skills', [])
        user_profile = UserProfile.objects.get(user=request.user)
        resources = fetch_gemini_resources(user_skills, 'legal support and worker rights')
        if not resources:
            resources = [{
                'title': 'Legal Aid for Freelancers',
                'description': 'Free legal advice for local freelancers.',
                'type': 'Legal',
                'url': 'https://www.example.com/legal-aid',
            }]
        return JsonResponse({'success': True, 'resources': resources})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def health_resources_api(request):
    try:
        data = json.loads(request.body)
        user_skills = data.get('user_skills', [])
        user_profile = UserProfile.objects.get(user=request.user)
        resources = fetch_gemini_resources(user_skills, 'health and wellness support')
        if not resources:
            resources = [{
                'title': 'Local Health Center Finder',
                'description': 'Find free and low-cost health clinics near you.',
                'type': 'Health',
                'url': 'https://www.healthcare.gov/freelancers',
            }]
        return JsonResponse({'success': True, 'resources': resources})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def emergency_resources_api(request):
    try:
        data = json.loads(request.body)
        user_skills = data.get('user_skills', [])
        user_profile = UserProfile.objects.get(user=request.user)
        resources = fetch_gemini_resources(user_skills, 'emergency assistance and crisis support')
        if not resources:
            resources = [{
                'title': 'Emergency Hotline',
                'description': '24/7 emergency support for freelancers.',
                'type': 'Emergency',
                'url': 'tel:123-456-7890',
            }]
        return JsonResponse({'success': True, 'resources': resources})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

# Helper functions for API integrations (no changes needed)
def get_skill_recommendations_from_api(skill_type, user_skills, api_key, user_profile):
    """Get skill-based course recommendations from external APIs"""
    recommendations = []
    if skill_type == 'general' or 'cooking' in user_skills:
        recommendations.extend([
            {'title': 'Professional Cooking Fundamentals', 'description': 'Learn essential cooking techniques and kitchen management skills', 'platform': 'Coursera', 'duration': '8 weeks', 'level': 'Beginner', 'url': 'https://www.coursera.org/learn/cooking-fundamentals'},
            {'title': 'Culinary Arts Certificate Program', 'description': 'Comprehensive culinary training for professional development', 'platform': 'edX', 'duration': '12 weeks', 'level': 'Intermediate', 'url': 'https://www.edx.org/learn/culinary-arts'}
        ])
    if skill_type == 'general' or 'plumbing' in user_skills:
        recommendations.extend([
            {'title': 'Basic Plumbing Skills', 'description': 'Learn essential plumbing techniques and safety procedures', 'platform': 'Udemy', 'duration': '6 weeks', 'level': 'Beginner', 'url': 'https://www.udemy.com/course/basic-plumbing-skills'},
            {'title': 'Advanced Plumbing Systems', 'description': 'Master complex plumbing systems and troubleshooting', 'platform': 'LinkedIn Learning', 'duration': '10 weeks', 'level': 'Advanced', 'url': 'https://www.linkedin.com/learning/advanced-plumbing-systems'}
        ])
    if skill_type == 'general' or 'electrical' in user_skills:
        recommendations.extend([
            {'title': 'Electrical Wiring Fundamentals', 'description': 'Learn safe electrical wiring practices and codes', 'platform': 'Coursera', 'duration': '8 weeks', 'level': 'Beginner', 'url': 'https://www.coursera.org/learn/electrical-wiring'},
            {'title': 'Advanced Electrical Systems', 'description': 'Master complex electrical installations and maintenance', 'platform': 'edX', 'duration': '12 weeks', 'level': 'Advanced', 'url': 'https://www.edx.org/learn/advanced-electrical-systems'}
        ])
    recommendations.extend([
        {'title': 'Business Communication Skills', 'description': 'Improve your professional communication and client interaction', 'platform': 'LinkedIn Learning', 'duration': '4 weeks', 'level': 'All Levels', 'url': 'https://www.linkedin.com/learning/business-communication'},
        {'title': 'Customer Service Excellence', 'description': 'Learn to provide outstanding customer service and build client relationships', 'platform': 'Udemy', 'duration': '3 weeks', 'level': 'All Levels', 'url': 'https://www.udemy.com/course/customer-service-excellence'}
    ])
    return recommendations

def get_certification_links_from_api(skill_type, user_skills, api_key, user_profile):
    """Get certification program links from external APIs"""
    certifications = []
    if skill_type == 'general' or 'cooking' in user_skills:
        certifications.extend([
            {'title': 'ServSafe Food Handler Certification', 'description': 'Essential food safety certification for food service workers', 'provider': 'ServSafe', 'duration': '2-4 hours', 'cost': '15', 'url': 'https://www.servsafe.com/food-handler', 'enroll_url': 'https://www.servsafe.com/food-handler/enroll'},
            {'title': 'Culinary Arts Professional Certificate', 'description': 'Comprehensive culinary training for professional development', 'provider': 'American Culinary Federation', 'duration': '6 months', 'cost': '500', 'url': 'https://www.acfchefs.org/certification', 'enroll_url': 'https://www.acfchefs.org/certification/enroll'}
        ])
    if skill_type == 'general' or 'plumbing' in user_skills:
        certifications.extend([
            {'title': 'Plumbing Apprentice Certification', 'description': 'Entry-level plumbing certification for apprentices', 'provider': 'Plumbing-Heating-Cooling Contractors Association', 'duration': '1 year', 'cost': '300', 'url': 'https://www.phccweb.org/certification', 'enroll_url': 'https://www.phccweb.org/certification/enroll'},
            {'title': 'Journeyman Plumber License', 'description': 'Professional plumbing license for experienced workers', 'provider': 'State Licensing Board', 'duration': '4 years', 'cost': '200', 'url': 'https://www.state.gov/plumbing-license', 'enroll_url': 'https://www.state.gov/plumbing-license/apply'}
        ])
    if skill_type == 'general' or 'electrical' in user_skills:
        certifications.extend([
            {'title': 'Electrical Apprentice Certification', 'description': 'Entry-level electrical certification for apprentices', 'provider': 'National Electrical Contractors Association', 'duration': '1 year', 'cost': '250', 'url': 'https://www.necanet.org/certification', 'enroll_url': 'https://www.necanet.org/certification/enroll'},
            {'title': 'Journeyman Electrician License', 'description': 'Professional electrical license for experienced workers', 'provider': 'State Licensing Board', 'duration': '4 years', 'cost': '180', 'url': 'https://www.state.gov/electrical-license', 'enroll_url': 'https://www.state.gov/electrical-license/apply'}
        ])
    certifications.extend([
        {'title': 'Customer Service Professional Certification', 'description': 'Professional certification in customer service excellence', 'provider': 'Customer Service Institute', 'duration': '3 months', 'cost': '150', 'url': 'https://www.csi.org/certification', 'enroll_url': 'https://www.csi.org/certification/enroll'},
        {'title': 'Small Business Management Certificate', 'description': 'Certificate in small business management and entrepreneurship', 'provider': 'Small Business Administration', 'duration': '6 months', 'cost': '100', 'url': 'https://www.sba.gov/certification', 'enroll_url': 'https://www.sba.gov/certification/enroll'}
    ])
    return certifications

def get_online_learning_links_from_api(skill_type, user_skills, api_keys, user_profile):
    """Get online learning resources from multiple platforms"""
    resources = {
        'coursera': [],
        'udemy': [],
        'linkedin_learning': [],
        'youtube': []
    }
    if skill_type == 'general' or 'cooking' in user_skills:
        resources['coursera'].extend([
            {'title': 'Cooking Fundamentals', 'description': 'Learn basic cooking techniques and kitchen safety', 'type': 'Course', 'duration': '8 weeks', 'price': 'Free', 'url': 'https://www.coursera.org/learn/cooking-fundamentals'}
        ])
        resources['udemy'].extend([
            {'title': 'Professional Cooking Masterclass', 'description': 'Comprehensive cooking course for professional development', 'type': 'Course', 'duration': '15 hours', 'price': '$29.99', 'url': 'https://www.udemy.com/course/professional-cooking'}
        ])
        resources['youtube'].extend([
            {'title': 'Cooking Basics Playlist', 'description': 'Free cooking tutorials and tips', 'type': 'Video Series', 'duration': '5 hours', 'price': 'Free', 'url': 'https://www.youtube.com/playlist?list=cooking-basics'}
        ])
    if skill_type == 'general' or 'plumbing' in user_skills:
        resources['linkedin_learning'].extend([
            {'title': 'Plumbing Essentials', 'description': 'Essential plumbing skills and safety procedures', 'type': 'Course', 'duration': '6 hours', 'price': 'Free with LinkedIn Premium', 'url': 'https://www.linkedin.com/learning/plumbing-essentials'}
        ])
        resources['youtube'].extend([
            {'title': 'DIY Plumbing Guide', 'description': 'Step-by-step plumbing tutorials', 'type': 'Video Series', 'duration': '3 hours', 'price': 'Free', 'url': 'https://www.youtube.com/playlist?list=diy-plumbing'}
        ])
    if skill_type == 'general' or 'electrical' in user_skills:
        resources['coursera'].extend([
            {'title': 'Electrical Safety Fundamentals', 'description': 'Learn electrical safety and basic wiring', 'type': 'Course', 'duration': '6 weeks', 'price': 'Free', 'url': 'https://www.coursera.org/learn/electrical-safety'}
        ])
        resources['udemy'].extend([
            {'title': 'Electrical Wiring Complete Course', 'description': 'Complete guide to electrical wiring and installation', 'type': 'Course', 'duration': '12 hours', 'price': '$39.99', 'url': 'https://www.udemy.com/course/electrical-wiring-complete'}
        ])
    resources['linkedin_learning'].extend([
        {'title': 'Professional Communication', 'description': 'Improve your professional communication skills', 'type': 'Course', 'duration': '4 hours', 'price': 'Free with LinkedIn Premium', 'url': 'https://www.linkedin.com/learning/professional-communication'}
    ])
    resources['youtube'].extend([
        {'title': 'Business Skills for Freelancers', 'description': 'Essential business skills for independent workers', 'type': 'Video Series', 'duration': '2 hours', 'price': 'Free', 'url': 'https://www.youtube.com/playlist?list=business-skills-freelancers'}
    ])
    return resources

@login_required
def post_job(request):
    """Post a new job (recruiter only)"""
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        if user_profile.user_type != 'recruiter':
            messages.error(request, 'Only recruiters can post jobs.')
            return redirect('dashboard')
        
        if request.method == 'POST':
            form = JobForm(request.POST)
            if form.is_valid():
                job = form.save(commit=False)
                job.recruiter = user_profile
                job.save()
                messages.success(request, 'Job posted successfully!')
                return redirect('dashboard')
        else:
            form = JobForm()
        
        return render(request, 'freelancer_platform/post_job.html', {'form': form})
    
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('home')

@login_required
def job_detail(request, job_id):
    """View job details"""
    job = get_object_or_404(Job, id=job_id)
    user_profile = UserProfile.objects.get(user=request.user)
    
    # Check if user has already applied
    has_applied = Application.objects.filter(job=job, freelancer=user_profile).exists()
    
    # Check if user has already requested the job
    has_requested = False
    job_request = None
    if user_profile.user_type == 'freelancer':
        try:
            job_request = JobRequest.objects.get(job=job, freelancer=user_profile)
            has_requested = True
        except JobRequest.DoesNotExist:
            has_requested = False
    
    context = {
        'job': job,
        'user_profile': user_profile,
        'has_applied': has_applied,
        'has_requested': has_requested,
        'job_request': job_request,
    }
    return render(request, 'freelancer_platform/job_detail.html', context)

@login_required
def apply_job(request, job_id):
    """Apply for a job (freelancer only)"""
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        if user_profile.user_type != 'freelancer':
            messages.error(request, 'Only freelancers can apply for jobs.')
            return redirect('dashboard')
        
        job = get_object_or_404(Job, id=job_id)
        
        # Check if already applied
        if Application.objects.filter(job=job, freelancer=user_profile).exists():
            messages.warning(request, 'You have already applied for this job.')
            return redirect('job_detail', job_id=job_id)
        
        if request.method == 'POST':
            form = ApplicationForm(request.POST)
            if form.is_valid():
                application = form.save(commit=False)
                application.job = job
                application.freelancer = user_profile
                application.save()
                messages.success(request, 'Application submitted successfully!')
                return redirect('dashboard')
        else:
            form = ApplicationForm()
        
        context = {
            'form': form,
            'job': job,
        }
        return render(request, 'freelancer_platform/apply_job.html', context)
    
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('home')

@login_required
def view_applications(request, job_id):
    """View applications for a job (recruiter only)"""
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        if user_profile.user_type != 'recruiter':
            messages.error(request, 'Only recruiters can view applications.')
            return redirect('dashboard')
        
        job = get_object_or_404(Job, id=job_id, recruiter=user_profile)
        applications = Application.objects.filter(job=job)
        
        context = {
            'job': job,
            'applications': applications,
        }
        return render(request, 'freelancer_platform/view_applications.html', context)
    
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('home')

@login_required
def request_job(request, job_id):
    """Request a job assignment (freelancer only)"""
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        if user_profile.user_type != 'freelancer':
            messages.error(request, 'Only freelancers can request jobs.')
            return redirect('dashboard')
        
        job = get_object_or_404(Job, id=job_id, status='open')
        
        # Check if already requested
        if JobRequest.objects.filter(job=job, freelancer=user_profile).exists():
            messages.warning(request, 'You have already requested this job.')
            return redirect('job_detail', job_id=job_id)
        
        if request.method == 'POST':
            form = JobRequestForm(request.POST, request.FILES, freelancer=user_profile)
            if form.is_valid():
                job_request = form.save(commit=False)
                job_request.job = job
                job_request.freelancer = user_profile
                job_request.save()
                
                # Save many-to-many relationships
                form.save_m2m()
                
                messages.success(request, 'Job request sent successfully!')
                return redirect('dashboard')
        else:
            form = JobRequestForm(freelancer=user_profile)
        
        context = {
            'form': form,
            'job': job,
        }
        return render(request, 'freelancer_platform/request_job.html', context)
    
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('home')

@login_required
def view_job_requests(request, job_id):
    """View job requests for a job (recruiter only)"""
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        if user_profile.user_type != 'recruiter':
            messages.error(request, 'Only recruiters can view job requests.')
            return redirect('dashboard')
        
        job = get_object_or_404(Job, id=job_id, recruiter=user_profile)
        job_requests = JobRequest.objects.filter(job=job)
        
        context = {
            'job': job,
            'job_requests': job_requests,
        }
        return render(request, 'freelancer_platform/view_job_requests.html', context)
    
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('home')

@login_required
def approve_job_request(request, request_id):
    """Approve a job request (recruiter only)"""
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        if user_profile.user_type != 'recruiter':
            messages.error(request, 'Only recruiters can approve job requests.')
            return redirect('dashboard')
        
        job_request = get_object_or_404(JobRequest, id=request_id, job__recruiter=user_profile)
        job = job_request.job
        
        if job.status != 'open':
            messages.error(request, 'This job is no longer available.')
            return redirect('view_job_requests', job_id=job.id)
        
        # Assign the job to the freelancer
        job.assigned_freelancer = job_request.freelancer
        job.status = 'assigned'
        job.save()
        
        # Update the job request status
        job_request.status = 'approved'
        job_request.save()
        
        # Reject all other pending requests for this job
        JobRequest.objects.filter(job=job, status='pending').exclude(id=request_id).update(status='rejected')
        
        messages.success(request, f'Job assigned to {job_request.freelancer.user.get_full_name() or job_request.freelancer.user.username}')
        return redirect('view_job_requests', job_id=job.id)
    
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('home')

@login_required
def reject_job_request(request, request_id):
    """Reject a job request (recruiter only)"""
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        if user_profile.user_type != 'recruiter':
            messages.error(request, 'Only recruiters can reject job requests.')
            return redirect('dashboard')
        
        job_request = get_object_or_404(JobRequest, id=request_id, job__recruiter=user_profile)
        job_request.status = 'rejected'
        job_request.save()
        
        messages.success(request, 'Job request rejected.')
        return redirect('view_job_requests', job_id=job_request.job.id)
    
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('home')

@login_required
def freelancer_profile(request):
    """Freelancer profile management"""
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        if user_profile.user_type != 'freelancer':
            messages.error(request, 'Only freelancers can access this page.')
            return redirect('dashboard')
        
        if request.method == 'POST':
            form = FreelancerProfileForm(request.POST, request.FILES, instance=user_profile)
            if form.is_valid():
                form.save()
                messages.success(request, 'Profile updated successfully!')
                return redirect('freelancer_profile')
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f'{field}: {error}')
        else:
            form = FreelancerProfileForm(instance=user_profile)
        
        work_examples = WorkExample.objects.filter(freelancer=user_profile)
        
        context = {
            'form': form,
            'user_profile': user_profile,
            'work_examples': work_examples,
        }
        return render(request, 'freelancer_platform/freelancer_profile.html', context)
    
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('home')

@login_required
def recruiter_profile(request):
    """Recruiter profile: basic info and photo (no skills)."""
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        if user_profile.user_type != 'recruiter':
            messages.error(request, 'Only recruiters can access this page.')
            return redirect('dashboard')

        if request.method == 'POST':
            uform = RecruiterUserForm(request.POST, instance=request.user)
            pform = RecruiterProfileForm(request.POST, request.FILES, instance=user_profile)
            if uform.is_valid() and pform.is_valid():
                uform.save()
                pform.save()
                messages.success(request, 'Profile updated successfully!')
                return redirect('recruiter_profile')
            else:
                for field, errors in (uform.errors.items() or pform.errors.items()):
                    for error in errors:
                        messages.error(request, f'{field}: {error}')
        else:
            uform = RecruiterUserForm(instance=request.user)
            pform = RecruiterProfileForm(instance=user_profile)

        context = {
            'user_profile': user_profile,
            'uform': uform,
            'pform': pform,
        }
        return render(request, 'freelancer_platform/recruiter_profile.html', context)
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('home')

@login_required
def add_work_example(request):
    """Add work example (freelancer only)"""
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        if user_profile.user_type != 'freelancer':
            messages.error(request, 'Only freelancers can add work examples.')
            return redirect('dashboard')
        
        if request.method == 'POST':
            form = WorkExampleForm(request.POST, request.FILES)
            if form.is_valid():
                work_example = form.save(commit=False)
                work_example.freelancer = user_profile
                work_example.save()
                messages.success(request, 'Work example added successfully!')
                return redirect('freelancer_profile')
        else:
            form = WorkExampleForm()
        
        context = {
            'form': form,
        }
        return render(request, 'freelancer_platform/add_work_example.html', context)
    
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('home')

@login_required
def delete_work_example(request, example_id):
    """Delete work example (freelancer only)"""
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        if user_profile.user_type != 'freelancer':
            messages.error(request, 'Only freelancers can delete work examples.')
            return redirect('dashboard')
        
        work_example = get_object_or_404(WorkExample, id=example_id, freelancer=user_profile)
        work_example.delete()
        messages.success(request, 'Work example deleted successfully!')
        return redirect('freelancer_profile')
    
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('home')

@login_required
def skill_based_jobs(request):
    """Get skill-based job recommendations for freelancers"""
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        if user_profile.user_type != 'freelancer':
            messages.error(request, 'Only freelancers can access skill-based recommendations.')
            return redirect('dashboard')
        
        # Get freelancer's skills
        freelancer_skills = user_profile.get_skills_list() + user_profile.selected_skills
        
        # Find jobs that match the freelancer's skills
        matching_jobs = []
        for job in Job.objects.filter(status='open'):
            job_skills = [skill.strip().lower() for skill in job.required_skills.split(',')]
            match_score = get_job_matching_score(freelancer_skills, job_skills)
            if match_score >= 5:  # Only show jobs with decent match
                matching_jobs.append({
                    'job': job,
                    'match_score': match_score
                })
        
        # Sort by match score
        matching_jobs.sort(key=lambda x: x['match_score'], reverse=True)
        
        context = {
            'user_profile': user_profile,
            'matching_jobs': matching_jobs,
        }
        return render(request, 'freelancer_platform/skill_based_jobs.html', context)
    
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('home')

@login_required
def delete_job(request, job_id):
    """Delete a job - only if no approved requests or job period expired"""
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        if user_profile.user_type != 'recruiter':
            messages.error(request, 'Only recruiters can delete jobs.')
            return redirect('dashboard')
        
        job = get_object_or_404(Job, id=job_id, recruiter=user_profile)
        
        # Check if job can be deleted
        if not job.can_be_deleted():
            messages.error(request, f'Cannot delete this job: {job.get_deletion_status()}')
            return redirect('dashboard')
        
        # Delete the job
        job_title = job.title
        job.delete()
        messages.success(request, f'Job "{job_title}" has been deleted successfully.')
        
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found.')
    except Job.DoesNotExist:
        messages.error(request, 'Job not found or you do not have permission to delete it.')
    
    return redirect('dashboard')

# Payment and Escrow System Views
@login_required
def initiate_payment(request, job_request_id):
    """Initiate payment for an approved job request (recruiter only)"""
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        if user_profile.user_type != 'recruiter':
            messages.error(request, 'Only recruiters can initiate payments.')
            return redirect('dashboard')
        
        job_request = get_object_or_404(JobRequest, id=job_request_id, status='approved')
        
        # Check if payment already exists
        if hasattr(job_request, 'payment'):
            messages.warning(request, 'Payment already initiated for this job request.')
            return redirect('payment_detail', payment_id=job_request.payment.id)
        
        if request.method == 'POST':
            form = PaymentForm(request.POST)
            if form.is_valid():
                payment = form.save(commit=False)
                payment.job_request = job_request
                payment.recruiter = user_profile
                payment.freelancer = job_request.freelancer
                # Prefer user-provided amount; fallback to proposed_rate
                amount_input = form.cleaned_data.get('amount')
                computed_amount = amount_input if amount_input is not None else job_request.proposed_rate
                if computed_amount is None:
                    form.add_error('amount', 'Amount is required. Please enter an amount.')
                    context = {
                        'form': form,
                        'job_request': job_request,
                    }
                    return render(request, 'freelancer_platform/initiate_payment.html', context)
                payment.amount = computed_amount
                payment.save()
                
                # Create work tracking record
                WorkTracking.objects.create(
                    payment=payment,
                    freelancer=job_request.freelancer
                )
                
                messages.success(request, 'Payment initiated successfully! Please complete the payment to start the work.')
                return redirect('payment_detail', payment_id=payment.id)
        else:
            form = PaymentForm(initial={'amount': job_request.proposed_rate or 0})
        
        context = {
            'form': form,
            'job_request': job_request,
        }
        return render(request, 'freelancer_platform/initiate_payment.html', context)
    
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('home')

@login_required
def payment_detail(request, payment_id):
    """View payment details"""
    payment = get_object_or_404(Payment, id=payment_id)
    user_profile = UserProfile.objects.get(user=request.user)
    
    # Check if user has access to this payment
    if user_profile not in [payment.recruiter, payment.freelancer]:
        messages.error(request, 'You do not have access to this payment.')
        return redirect('dashboard')
    
    work_tracking = payment.work_tracking.first()
    complaints = payment.complaints.all()
    
    context = {
        'payment': payment,
        'work_tracking': work_tracking,
        'complaints': complaints,
        'user_profile': user_profile,
    }
    return render(request, 'freelancer_platform/payment_detail.html', context)

@login_required
def confirm_payment(request, payment_id):
    """Confirm payment completion (recruiter only)"""
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        if user_profile.user_type != 'recruiter':
            messages.error(request, 'Only recruiters can confirm payments.')
            return redirect('dashboard')
        
        payment = get_object_or_404(Payment, id=payment_id, recruiter=user_profile)
        
        if payment.status != 'pending':
            messages.warning(request, 'Payment is not in pending status.')
            return redirect('payment_detail', payment_id=payment.id)
        
        # In a real implementation, this would integrate with Razorpay
        # For now, we'll simulate payment completion
        from django.utils import timezone
        payment.status = 'completed'
        payment.paid_at = timezone.now()
        payment.save()
        
        messages.success(request, 'Payment confirmed! Work can now begin.')
        return redirect('payment_detail', payment_id=payment.id)
    
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('home')

@login_required
def release_payment(request, payment_id):
    """Release payment to freelancer (recruiter only)"""
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        if user_profile.user_type != 'recruiter':
            messages.error(request, 'Only recruiters can release payments.')
            return redirect('dashboard')
        
        payment = get_object_or_404(Payment, id=payment_id, recruiter=user_profile)
        
        if not payment.can_be_released():
            messages.error(request, 'Payment cannot be released at this time.')
            return redirect('payment_detail', payment_id=payment.id)
        
        if payment.release_payment():
            messages.success(request, 'Payment released to freelancer successfully!')
        else:
            messages.error(request, 'Failed to release payment.')
        
        return redirect('payment_detail', payment_id=payment.id)
    
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('home')

@login_required
def submit_work(request, payment_id):
    """Submit work completion (freelancer only)"""
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        if user_profile.user_type != 'freelancer':
            messages.error(request, 'Only freelancers can submit work.')
            return redirect('dashboard')
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('dashboard')
    
    payment = get_object_or_404(Payment, id=payment_id, freelancer=user_profile)
    
    # Check if payment is in correct status
    if payment.status not in ['paid', 'work_submitted']:
        messages.error(request, 'Work cannot be submitted at this time.')
        return redirect('freelancer_dashboard')
    
    # Get or create work tracking
    work_tracking, created = WorkTracking.objects.get_or_create(
        payment=payment,
        freelancer=user_profile,
        defaults={'status': 'not_started'}
    )
    
    if request.method == 'POST':
        form = WorkTrackingForm(request.POST, request.FILES, instance=work_tracking)
        if form.is_valid():
            work_tracking = form.save(commit=False)
            work_tracking.status = 'submitted'
            work_tracking.submitted_at = timezone.now()
            work_tracking.save()
            
            # Update payment status
            payment.status = 'work_submitted'
            payment.work_submitted_at = timezone.now()
            payment.save()
            
            messages.success(request, 'Work submitted successfully! Waiting for recruiter review.')
            return redirect('freelancer_dashboard')
    else:
        form = WorkTrackingForm(instance=work_tracking)
    
    context = {
        'form': form,
        'payment': payment,
        'work_tracking': work_tracking,
    }
    return render(request, 'freelancer_platform/submit_work.html', context)

@login_required
def review_work(request, payment_id):
    """Recruiter reviews and confirms work"""
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        if user_profile.user_type != 'recruiter':
            messages.error(request, 'Access denied. Recruiter privileges required.')
            return redirect('dashboard')
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('dashboard')
    
    payment = get_object_or_404(Payment, id=payment_id, recruiter=user_profile)
    
    # Check if payment is in correct status
    if payment.status not in ['work_submitted', 'work_confirmed']:
        messages.error(request, 'Work cannot be reviewed at this time.')
        return redirect('recruiter_dashboard')
    
    work_tracking = get_object_or_404(WorkTracking, payment=payment)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        recruiter_feedback = request.POST.get('recruiter_feedback', '')
        
        if action == 'approve':
            work_tracking.status = 'completed'
            work_tracking.reviewed_at = timezone.now()
            work_tracking.recruiter_feedback = recruiter_feedback
            work_tracking.save()
            
            # Update payment status
            payment.status = 'work_confirmed'
            payment.work_confirmed_at = timezone.now()
            payment.work_confirmed_by = user_profile
            payment.save()
            
            # Release payment
            payment.status = 'released'
            payment.released_at = timezone.now()
            payment.save()
            
            messages.success(request, 'Work approved and payment released to freelancer!')
            
        elif action == 'reject':
            work_tracking.status = 'rejected'
            work_tracking.reviewed_at = timezone.now()
            work_tracking.recruiter_feedback = recruiter_feedback
            work_tracking.save()
            
            messages.success(request, 'Work rejected. Freelancer will be notified to resubmit.')
            
        elif action == 'request_revision':
            work_tracking.status = 'revision_requested'
            work_tracking.reviewed_at = timezone.now()
            work_tracking.recruiter_feedback = recruiter_feedback
            work_tracking.revision_notes = recruiter_feedback
            work_tracking.save()
            
            messages.success(request, 'Revision requested. Freelancer will be notified.')
        
        return redirect('recruiter_dashboard')
    
    context = {
        'payment': payment,
        'work_tracking': work_tracking,
    }
    return render(request, 'freelancer_platform/review_work.html', context)

@login_required
def payment_history(request):
    """View payment history for both freelancers and recruiters"""
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('dashboard')
    
    if user_profile.user_type == 'freelancer':
        payments = Payment.objects.filter(freelancer=user_profile).order_by('-created_at')
    else:
        payments = Payment.objects.filter(recruiter=user_profile).order_by('-created_at')
    
    context = {
        'user_profile': user_profile,
        'payments': payments,
    }
    return render(request, 'freelancer_platform/payment_history.html', context)

@login_required
def file_complaint_general(request):
    """File a general complaint"""
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = ComplaintForm(request.POST)
        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.complainant = user_profile
            complaint.save()
            messages.success(request, 'Complaint filed successfully. We will review it shortly.')
            return redirect('my_complaints')
    else:
        form = ComplaintForm()
    
    my_complaints = Complaint.objects.filter(complainant=user_profile).order_by('-created_at')[:10]
    context = {
        'form': form,
        'user_profile': user_profile,
        'my_complaints': my_complaints,
    }
    return render(request, 'freelancer_platform/file_complaint.html', context)

@login_required
def file_complaint_for_job(request, job_id):
    """File a complaint for a specific job"""
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('dashboard')
    
    job = get_object_or_404(Job, id=job_id)
    
    # Check if user has a payment for this job
    if user_profile.user_type == 'freelancer':
        payment = Payment.objects.filter(job_request__job=job, freelancer=user_profile).first()
    else:
        payment = Payment.objects.filter(job_request__job=job, recruiter=user_profile).first()
    
    if not payment:
        messages.error(request, 'No payment found for this job.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = ComplaintForm(request.POST, request.FILES, user_type=user_profile.user_type)
        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.payment = payment
            complaint.complainant = user_profile
            complaint.save()
            
            messages.success(request, 'Complaint filed successfully! Admin will review it soon.')
            return redirect('my_complaints')
    else:
        form = ComplaintForm(user_type=user_profile.user_type)
    
    my_complaints = Complaint.objects.filter(complainant=user_profile).order_by('-created_at')[:10]
    context = {
        'form': form,
        'job': job,
        'payment': payment,
        'my_complaints': my_complaints,
    }
    return render(request, 'freelancer_platform/file_complaint.html', context)

@login_required
def payment_test(request):
    """Payment testing interface"""
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('dashboard')
    
    # Get payment statistics
    if user_profile.user_type == 'freelancer':
        payments = Payment.objects.filter(freelancer=user_profile)
    else:
        payments = Payment.objects.filter(recruiter=user_profile)
    
    # Payment method breakdown
    payment_methods = {}
    for method, _ in Payment.PAYMENT_METHOD:
        count = payments.filter(payment_method=method).count()
        if count > 0:
            payment_methods[method] = count
    
    # Status breakdown
    status_counts = {}
    for status, _ in Payment.PAYMENT_STATUS:
        count = payments.filter(status=status).count()
        if count > 0:
            status_counts[status] = count
    
    context = {
        'user_profile': user_profile,
        'total_payments': payments.count(),
        'payment_methods': payment_methods,
        'status_counts': status_counts,
    }
    return render(request, 'freelancer_platform/payment_test.html', context)

@login_required
def chat_page(request, other_user_id):
    """
    Renders the chat page between the current user and another user.
    """
    other_user = get_object_or_404(User, id=other_user_id)
    context = {
        'other_user_id': other_user_id,
        'other_user_name': other_user.get_full_name() or other_user.username
    }
    return render(request, 'freelancer_platform/chat_app.html', context)

@login_required
@csrf_exempt
def send_message(request):
    """
    Handles an AJAX POST request to send a new message.
    It expects a JSON payload with 'receiver_id' and 'message_content'.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            receiver_id = data.get('receiver_id')
            message_content = data.get('message_content')
            
            # Ensure both receiver and message content are provided
            if not receiver_id or not message_content:
                return JsonResponse({'success': False, 'error': 'Missing receiver or message content'}, status=400)

            # Get the receiver User object or return a 404 error
            receiver = get_object_or_404(User, id=receiver_id)

            # Create and save the new message
            Message.objects.create(
                sender=request.user,
                receiver=receiver,
                message_content=message_content
            )

            # Return a success response
            return JsonResponse({'success': True, 'message': 'Message sent successfully'})
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON format'}, status=400)
    
    # Return an error if the request method is not POST
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)

@login_required
def get_messages(request, user_id):
    """
    Handles an AJAX GET request to retrieve messages between the current
    user and a specified other user.
    """
    try:
        # Get the other user based on the ID from the URL
        other_user = get_object_or_404(User, id=user_id)

        # Query for all messages where the current user and the other user
        # are either the sender or receiver. The Q object is used to
        # combine these conditions.
        messages = Message.objects.filter(
            Q(sender=request.user, receiver=other_user) | 
            Q(sender=other_user, receiver=request.user)
        ).select_related('sender', 'receiver') # Optimize with select_related

        # Serialize the messages into a list of dictionaries for the JSON response
        message_list = []
        for msg in messages:
            message_list.append({
                'sender': msg.sender.username,
                'receiver': msg.receiver.username,
                'message_content': msg.message_content,
                'timestamp': msg.timestamp.isoformat() # ISO format for easy parsing in JS
            })

        # Return the list of messages in a JSON response
        return JsonResponse({'success': True, 'messages': message_list})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
    
def messages_list_view(request):
    # Get all users except the current user
    user_profiles = UserProfile.objects.exclude(user=request.user)
    return render(request, 'freelancer_platform/messages_list.html', {'user_profiles': user_profiles})

@login_required
def workspace_detail(request):
    # Get the correct UserProfile instance
    user_profile = UserProfile.objects.get(user=request.user)

    # Fetch approved jobs for this freelancer profile
    approved_jobs = Application.objects.filter(freelancer=user_profile, status='approved').select_related('job')

    return render(request, 'freelancer_platform/workspace_detail.html', {'approved_jobs': approved_jobs})

@login_required
def file_complaint(request, payment_id):
    """File a complaint for a specific payment (both recruiter and freelancer)"""
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        payment = get_object_or_404(Payment, id=payment_id)
        
        # Check if user has access to this payment
        if user_profile not in [payment.recruiter, payment.freelancer]:
            messages.error(request, 'You do not have access to this payment.')
            return redirect('dashboard')
        
        # Check if complaint already exists
        existing_complaint = Complaint.objects.filter(payment=payment, complainant=user_profile).first()
        if existing_complaint:
            messages.warning(request, 'You have already filed a complaint for this payment.')
            return redirect('complaint_detail', complaint_id=existing_complaint.id)
        
        if request.method == 'POST':
            form = ComplaintForm(request.POST, request.FILES, user_type=user_profile.user_type)
            if form.is_valid():
                complaint = form.save(commit=False)
                complaint.payment = payment
                complaint.complainant = user_profile
                complaint.save()
                
                # Update payment status to disputed
                payment.status = 'disputed'
                payment.save()
                
                messages.success(request, 'Complaint filed successfully! Admin will review it soon.')
                return redirect('complaint_detail', complaint_id=complaint.id)
        else:
            form = ComplaintForm(user_type=user_profile.user_type)
        
        # Fetch user's complaints for side panel
        my_complaints = Complaint.objects.filter(complainant=user_profile).order_by('-created_at')[:10]
        context = {
            'form': form,
            'payment': payment,
            'user_profile': user_profile,
            'my_complaints': my_complaints,
        }
        return render(request, 'freelancer_platform/file_complaint.html', context)
    
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('home')

@login_required
def complaint_detail(request, complaint_id):
    """View complaint details"""
    complaint = get_object_or_404(Complaint, id=complaint_id)
    user_profile = UserProfile.objects.get(user=request.user)
    
    # Check if user has access to this complaint
    if user_profile not in [complaint.complainant, complaint.payment.recruiter, complaint.payment.freelancer]:
        messages.error(request, 'You do not have access to this complaint.')
        return redirect('dashboard')
    
    context = {
        'complaint': complaint,
        'user_profile': user_profile,
    }
    return render(request, 'freelancer_platform/complaint_detail.html', context)

@login_required
def my_complaints(request):
    """View user's complaints"""
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        complaints = Complaint.objects.filter(complainant=user_profile).order_by('-created_at')
        
        context = {
            'complaints': complaints,
            'user_profile': user_profile,
        }
        return render(request, 'freelancer_platform/my_complaints.html', context)
    
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('home')

@login_required
def admin_complaints(request):
    """Admin view for managing complaints"""
    if not request.user.is_staff:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('dashboard')
    
    complaints = Complaint.objects.filter(status__in=['open', 'under_review']).order_by('-created_at')
    
    context = {
        'complaints': complaints,
    }
    return render(request, 'freelancer_platform/admin_complaints.html', context)

@login_required
def resolve_complaint(request, complaint_id):
    """Resolve complaint (admin only)"""
    if not request.user.is_staff:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('dashboard')
    
    complaint = get_object_or_404(Complaint, id=complaint_id)
    
    if request.method == 'POST':
        form = AdminComplaintResolutionForm(request.POST)
        if form.is_valid():
            resolution_type = form.cleaned_data['resolution_type']
            admin_notes = form.cleaned_data['admin_notes']
            resolution_amount = form.cleaned_data['resolution_amount']
            
            complaint.resolve_complaint(request.user, resolution_type, admin_notes, resolution_amount)
            messages.success(request, 'Complaint resolved successfully!')
            return redirect('admin_complaints')
    else:
        form = AdminComplaintResolutionForm()
    
    context = {
        'form': form,
        'complaint': complaint,
    }
    return render(request, 'freelancer_platform/resolve_complaint.html', context)