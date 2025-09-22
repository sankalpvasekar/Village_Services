from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class UserProfile(models.Model):
    USER_TYPES = [
        ('freelancer', 'Freelancer'),
        ('recruiter', 'Job Recruiter'),
    ]
    
    SKILL_CATEGORIES = [
        ('cooking', 'Cooking'),
        ('salon', 'Salon/Beauty'),
        ('mechanical', 'Mechanical'),
        ('tailoring', 'Tailoring'),
        ('wireman', 'Electrical/Wiring'),
        ('cleaning', 'Cleaning'),
        ('plumbing', 'Plumbing'),
        ('carpentry', 'Carpentry'),
        ('painting', 'Painting'),
        ('gardening', 'Gardening'),
        ('other', 'Other'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=10, choices=USER_TYPES)
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    upi_id = models.CharField(max_length=100, blank=True, null=True, help_text="UPI ID for receiving payments")
    qr_code = models.ImageField(upload_to='payments/qr_codes/', blank=True, null=True, help_text="QR code image for payments")
    bank_account_name = models.CharField(max_length=100, blank=True, null=True, help_text="Name on bank account")
    bank_account_number = models.CharField(max_length=34, blank=True, null=True, help_text="Bank account number")
    bank_ifsc = models.CharField(max_length=20, blank=True, null=True, help_text="IFSC / Bank identifier")
    bank_name = models.CharField(max_length=100, blank=True, null=True, help_text="Bank name")
    skills = models.TextField(blank=True, null=True, help_text="Comma-separated list of skills")
    selected_skills = models.JSONField(default=list, blank=True, help_text="Selected skills from categories")
    experience_years = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(50)])
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.user_type}"
    
    def get_skills_list(self):
        """Return skills as a list"""
        if self.skills:
            return [skill.strip() for skill in self.skills.split(',')]
        return []
    
    def get_selected_skills_display(self):
        """Return selected skills as readable text"""
        if self.selected_skills:
            skill_names = [dict(UserProfile.SKILL_CATEGORIES)[skill] for skill in self.selected_skills if skill in dict(UserProfile.SKILL_CATEGORIES)]
            return ', '.join(skill_names)
        return ""
    
    def save(self, *args, **kwargs):
        # Delete old profile picture if a new one is being uploaded
        if self.pk:  # Only for existing instances
            try:
                old_instance = UserProfile.objects.get(pk=self.pk)
                if old_instance.profile_picture and self.profile_picture and old_instance.profile_picture != self.profile_picture:
                    # Delete the old file
                    old_instance.profile_picture.delete(save=False)
            except UserProfile.DoesNotExist:
                pass
        super().save(*args, **kwargs)

class WorkExample(models.Model):
    WORK_TYPES = [
        ('photo', 'Photo'),
        ('video', 'Video'),
        ('vr_video', 'VR Video'),
    ]
    
    freelancer = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='work_examples')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    work_type = models.CharField(max_length=10, choices=WORK_TYPES)
    file = models.FileField(upload_to='work_examples/', help_text="Upload photos, videos, or VR videos")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.freelancer.user.username} - {self.title}"
    
    class Meta:
        ordering = ['-created_at']

class Job(models.Model):
    JOB_CATEGORIES = [
        ('cooking', 'Cooking'),
        ('salon', 'Salon/Beauty'),
        ('mechanical', 'Mechanical'),
        ('tailoring', 'Tailoring'),
        ('wireman', 'Electrical/Wiring'),
        ('cleaning', 'Cleaning'),
        ('plumbing', 'Plumbing'),
        ('carpentry', 'Carpentry'),
        ('painting', 'Painting'),
        ('gardening', 'Gardening'),
        ('other', 'Other'),
    ]
    
    DURATION_UNITS = [
        ('days', 'Days'),
        ('weeks', 'Weeks'),
        ('months', 'Months'),
        ('years', 'Years'),
    ]
    
    JOB_STATUS = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('assigned', 'Assigned'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=JOB_CATEGORIES)
    company_name = models.CharField(max_length=200, blank=True, null=True)
    location = models.CharField(max_length=200, blank=True, null=True)
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    salary_max = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    required_skills = models.TextField()
    duration_months = models.IntegerField(default=1, help_text="Duration value")
    duration_unit = models.CharField(max_length=10, choices=DURATION_UNITS, default='months', help_text="Duration unit")
    workers_needed = models.IntegerField(default=1, validators=[MinValueValidator(1)], help_text="Number of workers needed")
    status = models.CharField(max_length=15, choices=JOB_STATUS, default='open')
    recruiter = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='posted_jobs')
    assigned_freelancer = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_jobs')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.expires_at and self.duration_months:
            from datetime import datetime, timedelta
            self.expires_at = datetime.now() + timedelta(days=self.duration_months * 30)
        super().save(*args, **kwargs)
    
    def can_be_deleted(self):
        """
        Check if the job can be deleted by the recruiter.
        Rules:
        - If any job request is approved, it cannot be deleted (unless mutual cancel flow implemented later).
        - Otherwise it can be deleted.
        """
        # Any approved request forbids deletion
        has_approved_request = self.job_requests.filter(status='approved').exists()
        return not has_approved_request
    
    def get_deletion_status(self):
        """Human-readable deletion status based on current rules."""
        if self.job_requests.filter(status='approved').exists():
            return "Has approved requests - cannot be deleted"
        return "No approved requests - can be deleted"

class Application(models.Model):
    APPLICATION_STATUS = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('withdrawn', 'Withdrawn'),
    ]
    
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    freelancer = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='job_applications')
    cover_letter = models.TextField(blank=True, null=True)
    proposed_rate = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=15, choices=APPLICATION_STATUS, default='pending')
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['job', 'freelancer']
    
    def __str__(self):
        return f"{self.freelancer.user.username} - {self.job.title}"

class JobRequest(models.Model):
    REQUEST_STATUS = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    PROPOSAL_TYPE = [
        ('monthly', 'Monthly'),
        ('daily', 'Daily'),
        ('hourly', 'Hourly'),
        ('fixed', 'Fixed Project'),
    ]
    
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='job_requests')
    freelancer = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='sent_requests')
    
    # Cover letter with microphone input support
    cover_letter = models.TextField(blank=True, null=True, help_text="Your proposal message. You can also record audio.")
    cover_letter_audio = models.FileField(upload_to='job_requests/audio/', blank=True, null=True, help_text="Record your cover letter via microphone")
    
    # Proposal details
    proposal_type = models.CharField(max_length=10, choices=PROPOSAL_TYPE, default='monthly')
    proposed_rate = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text="Your proposed rate")
    proposed_duration = models.IntegerField(blank=True, null=True, help_text="Duration in the selected unit (months/days/hours)")
    
    # Work examples and certificates
    selected_work_examples = models.ManyToManyField(WorkExample, blank=True, help_text="Select your previous work samples")
    certificates = models.FileField(upload_to='job_requests/certificates/', blank=True, null=True, help_text="Upload relevant certificates")
    
    status = models.CharField(max_length=15, choices=REQUEST_STATUS, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['job', 'freelancer']
    
    def __str__(self):
        return f"{self.freelancer.user.username} - {self.job.title}"
    
    def get_proposal_display(self):
        """Get formatted proposal rate display"""
        if self.proposal_type == 'monthly':
            return f"₹{self.proposed_rate}/month for {self.proposed_duration} months"
        elif self.proposal_type == 'daily':
            return f"₹{self.proposed_rate}/day for {self.proposed_duration} days"
        elif self.proposal_type == 'hourly':
            return f"₹{self.proposed_rate}/hour for {self.proposed_duration} hours"
        else:
            return f"₹{self.proposed_rate} (fixed project)"

class Payment(models.Model):
    PAYMENT_STATUS = [
        ('pending', 'Pending'),
        ('paid', 'Paid (In Escrow)'),
        ('work_submitted', 'Work Submitted'),
        ('work_confirmed', 'Work Confirmed'),
        ('released', 'Released to Freelancer'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
        ('disputed', 'Disputed'),
    ]
    
    PAYMENT_METHOD = [
        ('razorpay', 'Razorpay'),
        ('upi', 'UPI'),
        ('scanner', 'QR Scanner'),
        ('cash', 'Cash'),
        ('bank_transfer', 'Bank Transfer'),
    ]
    
    job_request = models.OneToOneField(JobRequest, on_delete=models.CASCADE, related_name='payment')
    recruiter = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='payments_made')
    freelancer = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='payments_received')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD, default='razorpay')
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    
    # Razorpay specific fields
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=200, blank=True, null=True)
    
    # Escrow fields
    is_escrow = models.BooleanField(default=True)
    escrow_release_date = models.DateTimeField(null=True, blank=True)
    
    # Work confirmation fields
    work_submitted_at = models.DateTimeField(null=True, blank=True)
    work_confirmed_at = models.DateTimeField(null=True, blank=True)
    work_confirmed_by = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='confirmed_work')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    released_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Payment {self.id} - ₹{self.amount} - {self.status}"
    
    def can_be_released(self):
        """Check if payment can be released to freelancer"""
        return (self.status == 'completed' and 
                self.is_escrow and 
                not self.released_at and
                self.work_tracking.exists() and
                self.work_tracking.filter(status='completed').exists())
    
    def release_payment(self):
        """Release payment to freelancer"""
        if self.can_be_released():
            from django.utils import timezone
            self.status = 'completed'
            self.released_at = timezone.now()
            self.save()
            return True
        return False

class WorkTracking(models.Model):
    WORK_STATUS = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('submitted', 'Submitted for Review'),
        ('completed', 'Completed & Confirmed'),
        ('rejected', 'Rejected by Recruiter'),
        ('revision_requested', 'Revision Requested'),
    ]
    
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='work_tracking')
    freelancer = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='work_submissions')
    status = models.CharField(max_length=20, choices=WORK_STATUS, default='not_started')
    
    # Work completion details
    completion_notes = models.TextField(blank=True, null=True)
    before_photos = models.FileField(upload_to='work_tracking/before/', blank=True, null=True, help_text="Before work photos")
    after_photos = models.FileField(upload_to='work_tracking/after/', blank=True, null=True, help_text="After work photos")
    completion_video = models.FileField(upload_to='work_tracking/videos/', blank=True, null=True, help_text="Completion video")
    
    # Additional work files
    work_files = models.FileField(upload_to='work_tracking/files/', blank=True, null=True, help_text="Additional work files")
    
    # Review fields
    recruiter_feedback = models.TextField(blank=True, null=True)
    revision_notes = models.TextField(blank=True, null=True)
    
    # Timestamps
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Work Tracking {self.id} - {self.status}"
    
    def mark_as_completed(self, notes=None, before_photos=None, after_photos=None, completion_video=None):
        """Mark work as completed by freelancer"""
        from django.utils import timezone
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.submitted_at = timezone.now()
        
        if notes:
            self.completion_notes = notes
        if before_photos:
            self.before_photos = before_photos
        if after_photos:
            self.after_photos = after_photos
        if completion_video:
            self.completion_video = completion_video
            
        self.save()

class Complaint(models.Model):
    COMPLAINT_TYPES = [
        ('recruiter_payment', 'Recruiter: Paid but no work done'),
        ('recruiter_quality', 'Recruiter: Work quality is poor'),
        ('recruiter_delay', 'Recruiter: Work not completed on time'),
        ('freelancer_payment', 'Freelancer: Work done but no payment'),
        ('freelancer_delay', 'Freelancer: Payment delayed'),
        ('freelancer_escrow', 'Freelancer: Payment stuck in escrow'),
    ]
    
    COMPLAINT_STATUS = [
        ('open', 'Open'),
        ('under_review', 'Under Review'),
        ('resolved', 'Resolved'),
        ('rejected', 'Rejected'),
        ('escalated', 'Escalated'),
    ]
    
    RESOLUTION_TYPES = [
        ('refund_recruiter', 'Refund to Recruiter'),
        ('release_payment', 'Release Payment to Freelancer'),
        ('partial_payment', 'Partial Payment'),
        ('no_action', 'No Action Required'),
        ('warning_issued', 'Warning Issued'),
    ]
    
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='complaints')
    complainant = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='complaints_filed')
    complaint_type = models.CharField(max_length=25, choices=COMPLAINT_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    # Evidence files
    evidence_photos = models.FileField(upload_to='complaints/evidence/', blank=True, null=True, help_text="Evidence photos")
    evidence_videos = models.FileField(upload_to='complaints/evidence/', blank=True, null=True, help_text="Evidence videos")
    evidence_documents = models.FileField(upload_to='complaints/evidence/', blank=True, null=True, help_text="Evidence documents")
    
    # Admin resolution
    status = models.CharField(max_length=15, choices=COMPLAINT_STATUS, default='open')
    admin_notes = models.TextField(blank=True, null=True)
    resolution_type = models.CharField(max_length=20, choices=RESOLUTION_TYPES, blank=True, null=True)
    resolution_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_complaints')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Complaint {self.id} - {self.title} - {self.status}"
    
    def resolve_complaint(self, admin_user, resolution_type, admin_notes=None, resolution_amount=None):
        """Resolve complaint by admin"""
        from django.utils import timezone
        self.status = 'resolved'
        self.resolution_type = resolution_type
        self.resolved_by = admin_user
        self.resolved_at = timezone.now()
        
        if admin_notes:
            self.admin_notes = admin_notes
        if resolution_amount:
            self.resolution_amount = resolution_amount
            
        self.save()
        
        # Execute resolution action
        if resolution_type == 'refund_recruiter':
            self.payment.status = 'refunded'
            self.payment.save()
        elif resolution_type == 'release_payment':
            self.payment.release_payment()
        elif resolution_type == 'partial_payment' and resolution_amount:
            # Handle partial payment logic here
            pass


class Message(models.Model):
    """
    Model to represent a private message between two users.
    
    The 'sender' is the user who created the message.
    The 'receiver' is the user who receives the message.
    The 'message_content' is the text of the message itself.
    The 'timestamp' records when the message was sent.
    """
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
        Returns a string representation of the message.
        """
        return f'Message from {self.sender.username} to {self.receiver.username} at {self.timestamp.strftime("%Y-%m-%d %H:%M:%S")}'

    class Meta:
        """
        Meta options for the Message model.
        """
        # Order messages by timestamp in ascending order
        ordering = ['timestamp']