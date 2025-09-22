from django.urls import path
from . import views
from .views import messages_list_view

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('post-job/', views.post_job, name='post_job'),
    path('job/<int:job_id>/', views.job_detail, name='job_detail'),
    path('job/<int:job_id>/apply/', views.apply_job, name='apply_job'),
    path('job/<int:job_id>/applications/', views.view_applications, name='view_applications'),
    path('job/<int:job_id>/request/', views.request_job, name='request_job'),
    path('job/<int:job_id>/requests/', views.view_job_requests, name='view_job_requests'),
    path('job-request/<int:request_id>/approve/', views.approve_job_request, name='approve_job_request'),
    path('job-request/<int:request_id>/reject/', views.reject_job_request, name='reject_job_request'),
    path('freelancer-profile/', views.freelancer_profile, name='freelancer_profile'),
    path('recruiter-profile/', views.recruiter_profile, name='recruiter_profile'),
    path('add-work-example/', views.add_work_example, name='add_work_example'),
    path('delete-work-example/<int:example_id>/', views.delete_work_example, name='delete_work_example'),
    path('skill-based-jobs/', views.skill_based_jobs, name='skill_based_jobs'),
    path('job/<int:job_id>/delete/', views.delete_job, name='delete_job'),
    
    # Payment and Escrow System URLs
    path('job-request/<int:job_request_id>/initiate-payment/', views.initiate_payment, name='initiate_payment'),
    path('payment/<int:payment_id>/', views.payment_detail, name='payment_detail'),
    path('payment/<int:payment_id>/confirm/', views.confirm_payment, name='confirm_payment'),
    path('payment/<int:payment_id>/release/', views.release_payment, name='release_payment'),
    path('payment/<int:payment_id>/submit-work/', views.submit_work, name='submit_work'),
    path('payment/<int:payment_id>/review-work/', views.review_work, name='review_work'),
    path('payment-history/', views.payment_history, name='payment_history'),
    # Removed payment testing route
    
    # Complaint System URLs
    path('file-complaint/', views.file_complaint_general, name='file_complaint_general'),
    path('payment/<int:payment_id>/file-complaint/', views.file_complaint, name='file_complaint'),
    path('job/<int:job_id>/file-complaint/', views.file_complaint_for_job, name='file_complaint_for_job'),
    path('workspace/', views.workspace_detail, name='workspace_detail'),
    path('complaint/<int:complaint_id>/', views.complaint_detail, name='complaint_detail'),
    path('my-complaints/', views.my_complaints, name='my_complaints'),
    
    # Admin URLs
    path('admin/complaints/', views.admin_complaints, name='admin_complaints'),
    path('admin/complaint/<int:complaint_id>/resolve/', views.resolve_complaint, name='resolve_complaint'),
    
    # API endpoints for skill-based recommendations
    path('api/skill-recommendations/', views.skill_recommendations_api, name='skill_recommendations_api'),
    path('api/certification-links/', views.certification_links_api, name='certification_links_api'),
    path('api/online-learning-links/', views.online_learning_links_api, name='online_learning_links_api'),
    path('api/financial-resources/', views.financial_resources_api, name='financial_resources_api'),
    path('api/community-resources/', views.community_resources_api, name='community_resources_api'),
    path('api/legal-resources/', views.legal_resources_api, name='legal_resources_api'),
    path('api/health-resources/', views.health_resources_api, name='health_resources_api'),
    path('api/emergency-resources/', views.emergency_resources_api, name='emergency_resources_api'),


    path('messages/', messages_list_view, name='messages_list'),
] 