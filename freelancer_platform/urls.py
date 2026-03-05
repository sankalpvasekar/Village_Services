# C:\Users\DDR\OneDrive\Documents\local_freelancer_final\Local_Free_Lancer_New\freelancer_platform\urls.py

from django.urls import path
from .views import (
    home, register, user_login, user_logout, login_redirect,
    freelancer_dashboard, recruiter_dashboard, post_job, job_detail,
    apply_job, view_applications, request_job, view_job_requests,
    approve_job_request, reject_job_request, freelancer_profile, recruiter_profile,
    add_work_example, delete_work_example, skill_based_jobs, delete_job,
    initiate_payment, payment_detail, confirm_payment, release_payment,
    submit_work, review_work, payment_history, file_complaint_general,
    file_complaint, file_complaint_for_job, complaint_detail, my_complaints,
    admin_complaints, resolve_complaint, skill_recommendations_api,
    certification_links_api, online_learning_links_api, financial_resources_api,
    community_resources_api, legal_resources_api, health_resources_api,
    emergency_resources_api, chat_page, send_message, get_messages,
    messages_list_view, workspace_detail, my_applications
)


urlpatterns = [
    path('', home, name='home'),
    path('register/', register, name='register'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    
    # Consolidated dashboard URLs for clarity and security
    path('dashboard/', login_redirect, name='dashboard'),
    path('login/redirect/', login_redirect, name='login_redirect'),
    
    # Specific dashboards
    path('freelancer/dashboard/', freelancer_dashboard, name='freelancer_dashboard'),
    path('recruiter/dashboard/', recruiter_dashboard, name='recruiter_dashboard'),
    
    path('post-job/', post_job, name='post_job'),
    path('job/<int:job_id>/', job_detail, name='job_detail'),
    path('job/<int:job_id>/apply/', apply_job, name='apply_job'),
    path('job/<int:job_id>/applications/', view_applications, name='view_applications'),
    path('job/<int:job_id>/request/', request_job, name='request_job'),
    path('job/<int:job_id>/requests/', view_job_requests, name='view_job_requests'),
    path('job-request/<int:request_id>/approve/', approve_job_request, name='approve_job_request'),
    path('job-request/<int:request_id>/reject/', reject_job_request, name='reject_job_request'),
    path('freelancer-profile/', freelancer_profile, name='freelancer_profile'),
    path('recruiter-profile/', recruiter_profile, name='recruiter_profile'),
    path('add-work-example/', add_work_example, name='add_work_example'),
    path('delete-work-example/<int:example_id>/', delete_work_example, name='delete_work_example'),
    path('skill-based-jobs/', skill_based_jobs, name='skill_based_jobs'),
    path('job/<int:job_id>/delete/', delete_job, name='delete_job'),
    
    # Payment and Escrow System URLs
    path('job-request/<int:job_request_id>/initiate-payment/', initiate_payment, name='initiate_payment'),
    path('payment/<int:payment_id>/', payment_detail, name='payment_detail'),
    path('payment/<int:payment_id>/confirm/', confirm_payment, name='confirm_payment'),
    path('payment/<int:payment_id>/release/', release_payment, name='release_payment'),
    path('payment/<int:payment_id>/submit-work/', submit_work, name='submit_work'),
    path('payment/<int:payment_id>/review-work/', review_work, name='review_work'),
    path('payment-history/', payment_history, name='payment_history'),
    path('my-applications/', my_applications, name='my_applications'),
    
    # Complaint System URLs
    path('file-complaint/', file_complaint_general, name='file_complaint_general'),
    path('payment/<int:payment_id>/file-complaint/', file_complaint, name='file_complaint'),
    path('job/<int:job_id>/file-complaint/', file_complaint_for_job, name='file_complaint_for_job'),
    path('workspace/', workspace_detail, name='workspace_detail'),
    path('complaint/<int:complaint_id>/', complaint_detail, name='complaint_detail'),
    path('my-complaints/', my_complaints, name='my_complaints'),
    
    # Admin URLs
    path('admin/complaints/', admin_complaints, name='admin_complaints'),
    path('admin/complaint/<int:complaint_id>/resolve/', resolve_complaint, name='resolve_complaint'),
    
    # API endpoints for skill-based recommendations
    path('api/skill-recommendations/', skill_recommendations_api, name='skill_recommendations_api'),
    path('api/certification-links/', certification_links_api, name='certification_links_api'),
    path('api/online-learning-links/', online_learning_links_api, name='online_learning_links_api'),
    path('api/financial-resources/', financial_resources_api, name='financial_resources_api'),
    path('api/community-resources/', community_resources_api, name='community_resources_api'),
    path('api/legal-resources/', legal_resources_api, name='legal_resources_api'),
    path('api/health-resources/', health_resources_api, name='health_resources_api'),
    path('api/emergency-resources/', emergency_resources_api, name='emergency_resources_api'),

    path('messages/', messages_list_view, name='messages_list'),
    path('chat/<int:other_user_id>/', chat_page, name='chat_page'),
    path('api/send-message/', send_message, name='send_message'),
    path('api/get-messages/<int:user_id>/', get_messages, name='get_messages'),
]