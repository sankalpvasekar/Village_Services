from django.contrib import admin
<<<<<<< HEAD

# Register your models here.
=======
from .models import UserProfile, Job, Application, JobRequest, WorkExample, Payment, WorkTracking, Complaint

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'user_type', 'phone', 'experience_years', 'hourly_rate', 'created_at']
    list_filter = ['user_type', 'created_at']
    search_fields = ['user__username', 'user__email', 'phone', 'skills']

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'recruiter', 'status', 'salary_min', 'salary_max', 'created_at']
    list_filter = ['category', 'status', 'created_at']
    search_fields = ['title', 'description', 'company_name', 'location']

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ['freelancer', 'job', 'status', 'proposed_rate', 'applied_at']
    list_filter = ['status', 'applied_at']
    search_fields = ['freelancer__user__username', 'job__title']

@admin.register(JobRequest)
class JobRequestAdmin(admin.ModelAdmin):
    list_display = ['freelancer', 'job', 'status', 'proposal_type', 'proposed_rate', 'created_at']
    list_filter = ['status', 'proposal_type', 'created_at']
    search_fields = ['freelancer__user__username', 'job__title']

@admin.register(WorkExample)
class WorkExampleAdmin(admin.ModelAdmin):
    list_display = ['freelancer', 'title', 'work_type', 'created_at']
    list_filter = ['work_type', 'created_at']
    search_fields = ['freelancer__user__username', 'title']

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'recruiter', 'freelancer', 'amount', 'status', 'payment_method', 'created_at']
    list_filter = ['status', 'payment_method', 'is_escrow', 'created_at']
    search_fields = ['recruiter__user__username', 'freelancer__user__username', 'razorpay_payment_id']
    readonly_fields = ['razorpay_payment_id', 'razorpay_order_id', 'razorpay_signature', 'created_at', 'updated_at']

@admin.register(WorkTracking)
class WorkTrackingAdmin(admin.ModelAdmin):
    list_display = ['id', 'freelancer', 'payment', 'status', 'completed_at', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['freelancer__user__username', 'payment__id']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ['id', 'complainant', 'complaint_type', 'status', 'created_at', 'resolved_at']
    list_filter = ['complaint_type', 'status', 'created_at']
    search_fields = ['complainant__user__username', 'title', 'description']
    readonly_fields = ['created_at', 'updated_at', 'resolved_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('complainant__user', 'payment', 'resolved_by')
>>>>>>> 29d8db2d3b215d8409fd8145e93e0e02b2e12a74
