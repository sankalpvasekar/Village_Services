from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile, Job, Application, JobRequest, WorkExample, Payment, WorkTracking, Complaint

class UserRegistrationForm(UserCreationForm):
    USER_TYPES = [
        ('freelancer', 'Freelancer'),
        ('recruiter', 'Job Recruiter'),
    ]
    
    user_type = forms.ChoiceField(choices=USER_TYPES, widget=forms.Select(attrs={'class': 'form-select'}))
    phone = forms.CharField(max_length=15, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    address = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}), required=False)
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if hasattr(field, 'widget') and hasattr(field.widget, 'attrs'):
                field.widget.attrs.update({'class': 'form-control'})

class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['title', 'description', 'category', 'company_name', 'location', 'salary_min', 'salary_max', 'required_skills', 'duration_months', 'duration_unit']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'salary_min': forms.NumberInput(attrs={'class': 'form-control'}),
            'salary_max': forms.NumberInput(attrs={'class': 'form-control'}),
            'required_skills': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'duration_months': forms.NumberInput(attrs={'class': 'form-control'}),
            'duration_unit': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make fields optional
        self.fields['company_name'].required = False
        self.fields['location'].required = False
        self.fields['salary_min'].required = False
        self.fields['salary_max'].required = False

class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['proposed_rate']
        widgets = {
            'proposed_rate': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class JobRequestForm(forms.ModelForm):
    selected_work_examples = forms.ModelMultipleChoiceField(
        queryset=WorkExample.objects.none(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False,
        help_text="Select your previous work samples to showcase your skills"
    )
    
    class Meta:
        model = JobRequest
        fields = ['cover_letter', 'cover_letter_audio', 'proposal_type', 'proposed_rate', 'proposed_duration', 'selected_work_examples', 'certificates']
        widgets = {
            'cover_letter': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 5, 
                'placeholder': 'Explain why you are the best fit for this job... You can also record audio below.'
            }),
            'cover_letter_audio': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'audio/*',
                'data-audio-recorder': 'true'
            }),
            'proposal_type': forms.Select(attrs={'class': 'form-select'}),
            'proposed_rate': forms.NumberInput(attrs={'class': 'form-control'}),
            'proposed_duration': forms.NumberInput(attrs={'class': 'form-control'}),
            'certificates': forms.FileInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        freelancer = kwargs.pop('freelancer', None)
        super().__init__(*args, **kwargs)
        
        if freelancer:
            # Set the queryset for work examples to only show the freelancer's examples
            self.fields['selected_work_examples'].queryset = WorkExample.objects.filter(freelancer=freelancer)
        
        # Add help text for proposal fields
        self.fields['proposal_type'].help_text = "Choose how you want to charge for this job"
        self.fields['proposed_rate'].help_text = "Your proposed rate per unit (month/day/hour)"
        self.fields['proposed_duration'].help_text = "Duration in the selected unit"
        self.fields['certificates'].help_text = "Upload relevant certificates (optional)"

class FreelancerProfileForm(forms.ModelForm):
    selected_skills = forms.MultipleChoiceField(
        choices=UserProfile.SKILL_CATEGORIES,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False
    )
    
    class Meta:
        model = UserProfile
        fields = ['phone', 'address', 'skills', 'selected_skills', 'experience_years', 'hourly_rate', 'bio', 'profile_picture']
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'skills': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter additional skills (comma-separated)'}),
            'experience_years': forms.NumberInput(attrs={'class': 'form-control'}),
            'hourly_rate': forms.NumberInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'profile_picture': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
                'data-max-size': '5242880',  # 5MB in bytes
                'onchange': 'previewImage(this)'
            }),
        }
    
    def clean_profile_picture(self):
        profile_picture = self.cleaned_data.get('profile_picture')
        
        # Only validate if this is a new file upload (not an existing file)
        if profile_picture and hasattr(profile_picture, 'content_type'):
            # This is a new uploaded file
            # Check file size (5MB limit)
            if profile_picture.size > 5 * 1024 * 1024:  # 5MB in bytes
                raise forms.ValidationError("Profile picture must be less than 5MB.")
            
            # Check file type
            allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif']
            if profile_picture.content_type not in allowed_types:
                raise forms.ValidationError("Please upload a valid image file (JPG, PNG, or GIF).")
        
        return profile_picture

class WorkExampleForm(forms.ModelForm):
    class Meta:
        model = WorkExample
        fields = ['title', 'description', 'work_type', 'file']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'work_type': forms.Select(attrs={'class': 'form-select'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
        }

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['amount', 'payment_method']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'payment_method': forms.Select(attrs={'class': 'form-select'}),
        }

class WorkTrackingForm(forms.ModelForm):
    class Meta:
        model = WorkTracking
        fields = ['completion_notes', 'before_photos', 'after_photos', 'completion_video', 'work_files']
        widgets = {
            'completion_notes': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 5,
                'placeholder': 'Describe the work completed, any challenges faced, and final results...'
            }),
            'before_photos': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'after_photos': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'completion_video': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'video/*'
            }),
            'work_files': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx,.txt,.zip,.rar'
            }),
        }

class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['complaint_type', 'title', 'description', 'evidence_photos', 'evidence_videos', 'evidence_documents']
        widgets = {
            'complaint_type': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Brief title for your complaint'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 6,
                'placeholder': 'Please provide detailed information about your complaint. Include dates, amounts, and any relevant details...'
            }),
            'evidence_photos': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'evidence_videos': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'video/*'
            }),
            'evidence_documents': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx,.txt'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        user_type = kwargs.pop('user_type', None)
        super().__init__(*args, **kwargs)
        
        # Filter complaint types based on user type
        if user_type == 'recruiter':
            self.fields['complaint_type'].choices = [
                ('recruiter_payment', 'Paid but no work done'),
                ('recruiter_quality', 'Work quality is poor'),
            ]
        elif user_type == 'freelancer':
            self.fields['complaint_type'].choices = [
                ('freelancer_payment', 'Work done but no payment'),
                ('freelancer_delay', 'Payment delayed'),
            ]

class AdminComplaintResolutionForm(forms.Form):
    resolution_type = forms.ChoiceField(
        choices=Complaint.RESOLUTION_TYPES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    admin_notes = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control', 
            'rows': 4,
            'placeholder': 'Admin notes about the resolution...'
        }),
        required=False
    )
    resolution_amount = forms.DecimalField(
        max_digits=10, 
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        required=False,
        help_text="Required for partial payment resolution"
    ) 