# freelancer_platform/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile, Job, Application, JobRequest, WorkExample, Payment, WorkTracking, Complaint

# --- Custom Widget Classes for a Light-Themed Input on a Dark Page ---
# These classes make the input background white, text black, and have a subtle border/focus.

# General text, email, number inputs
LIGHT_INPUT_CLASSES = 'w-full px-4 py-2 rounded-md bg-white border border-gray-300 text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500'

# Textarea inputs (inherits from LIGHT_INPUT_CLASSES and adds height)
LIGHT_TEXTAREA_CLASSES = LIGHT_INPUT_CLASSES + ' min-h-[100px]'

# Select inputs
LIGHT_SELECT_CLASSES = 'w-full px-4 py-2 rounded-md bg-white border border-gray-300 text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500'

# File inputs (visually hidden, with a custom label/display in HTML)
HIDDEN_FILE_INPUT_CLASSES = 'file-input-hidden'

# --- Form Definitions ---

class UserRegistrationForm(UserCreationForm):
    USER_TYPES = [
        ('freelancer', 'Freelancer'),
        ('recruiter', 'Job Recruiter'),
    ]
    
    user_type = forms.ChoiceField(choices=USER_TYPES, widget=forms.Select(attrs={'class': LIGHT_SELECT_CLASSES}))
    phone = forms.CharField(max_length=15, required=False, widget=forms.TextInput(attrs={'class': LIGHT_INPUT_CLASSES, 'placeholder': 'Phone Number'}))
    address = forms.CharField(widget=forms.Textarea(attrs={'class': LIGHT_TEXTAREA_CLASSES, 'rows': 3, 'placeholder': 'Your Address'}), required=False)
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': LIGHT_INPUT_CLASSES, 'placeholder': 'Username'}),
            'first_name': forms.TextInput(attrs={'class': LIGHT_INPUT_CLASSES, 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': LIGHT_INPUT_CLASSES, 'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'class': LIGHT_INPUT_CLASSES, 'placeholder': 'Email Address'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Apply default LIGHT_INPUT_CLASSES to all fields that aren't explicitly styled above
        # This loop iterates over the bound fields after Meta.widgets have been applied.
        # It's less common to do this if you explicitly style all fields in Meta.widgets.
        # Given your explicit widgets, this loop might be redundant for some fields but safe.
        for field_name, field in self.fields.items():
            if field_name not in ['user_type', 'phone', 'address'] and hasattr(field, 'widget') and hasattr(field.widget, 'attrs'):
                if 'class' not in field.widget.attrs:
                    field.widget.attrs['class'] = LIGHT_INPUT_CLASSES
                else:
                    field.widget.attrs['class'] += f' {LIGHT_INPUT_CLASSES}'


class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['title', 'description', 'category', 'company_name', 'location', 'salary_min', 'salary_max', 'required_skills', 'duration_months', 'duration_unit', 'workers_needed']
        widgets = {
            'title': forms.TextInput(attrs={'class': LIGHT_INPUT_CLASSES, 'placeholder': 'Job Title'}),
            'description': forms.Textarea(attrs={'class': LIGHT_TEXTAREA_CLASSES, 'rows': 5, 'placeholder': 'Detailed Job Description'}),
            'category': forms.Select(attrs={'class': LIGHT_SELECT_CLASSES}),
            'company_name': forms.TextInput(attrs={'class': LIGHT_INPUT_CLASSES, 'placeholder': 'Company Name'}),
            'location': forms.TextInput(attrs={'class': LIGHT_INPUT_CLASSES, 'placeholder': 'Job Location'}),
            'salary_min': forms.NumberInput(attrs={'class': LIGHT_INPUT_CLASSES, 'placeholder': 'Minimum Salary'}),
            'salary_max': forms.NumberInput(attrs={'class': LIGHT_INPUT_CLASSES, 'placeholder': 'Maximum Salary'}),
            'required_skills': forms.Textarea(attrs={'class': LIGHT_TEXTAREA_CLASSES + ' whitespace-nowrap overflow-x-auto min-h-[64px]', 'rows': 3, 'placeholder': 'Required skills (comma-separated, e.g. cooking,chapatmaking,currprepration,cleaning)'}),
            'duration_months': forms.NumberInput(attrs={'class': LIGHT_INPUT_CLASSES, 'placeholder': 'Duration'}),
            'duration_unit': forms.Select(attrs={'class': LIGHT_SELECT_CLASSES}),
            'workers_needed': forms.NumberInput(attrs={'class': LIGHT_INPUT_CLASSES, 'min': 1, 'placeholder': 'Number of Workers'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make fields optional (as per your original forms.py)
        self.fields['company_name'].required = False
        self.fields['location'].required = False
        self.fields['salary_min'].required = False
        self.fields['salary_max'].required = False

class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['proposed_rate']
        widgets = {
            'proposed_rate': forms.NumberInput(attrs={'class': LIGHT_INPUT_CLASSES, 'placeholder': 'Your Proposed Rate'}),
        }

class JobRequestForm(forms.ModelForm):
    selected_work_examples = forms.ModelMultipleChoiceField(
        queryset=WorkExample.objects.none(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input text-blue-600 bg-white border-gray-300 focus:ring-blue-500'}), # Tailored for checkboxes
        required=False,
        help_text="Select your previous work samples to showcase your skills"
    )
    
    class Meta:
        model = JobRequest
        fields = ['cover_letter', 'cover_letter_audio', 'proposal_type', 'proposed_rate', 'proposed_duration', 'selected_work_examples', 'certificates']
        widgets = {
            'cover_letter': forms.Textarea(attrs={
                'class': LIGHT_TEXTAREA_CLASSES, 
                'rows': 5, 
                'placeholder': 'Explain why you are the best fit for this job... You can also record audio below.'
            }),
            'cover_letter_audio': forms.FileInput(attrs={
                'class': HIDDEN_FILE_INPUT_CLASSES, # Use custom hidden input for styling
                'accept': 'audio/*',
                'data-audio-recorder': 'true'
            }),
            'proposal_type': forms.Select(attrs={'class': LIGHT_SELECT_CLASSES}),
            'proposed_rate': forms.NumberInput(attrs={'class': LIGHT_INPUT_CLASSES, 'placeholder': 'Your Proposed Rate'}),
            'proposed_duration': forms.NumberInput(attrs={'class': LIGHT_INPUT_CLASSES, 'placeholder': 'Proposed Duration'}),
            'certificates': forms.FileInput(attrs={'class': HIDDEN_FILE_INPUT_CLASSES, 'accept': '.pdf,.doc,.docx'}), # Use custom hidden input for styling
        }
    
    def __init__(self, *args, **kwargs):
        freelancer = kwargs.pop('freelancer', None)
        super().__init__(*args, **kwargs)
        
        if freelancer:
            self.fields['selected_work_examples'].queryset = WorkExample.objects.filter(freelancer=freelancer)
        
        self.fields['proposal_type'].help_text = "Choose how you want to charge for this job"
        self.fields['proposed_rate'].help_text = "Your proposed rate per unit (month/day/hour)"
        self.fields['proposed_duration'].help_text = "Duration in the selected unit"
        self.fields['certificates'].help_text = "Upload relevant certificates (optional)"

class FreelancerProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=150, required=False, widget=forms.TextInput(attrs={'class': LIGHT_INPUT_CLASSES, 'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=150, required=False, widget=forms.TextInput(attrs={'class': LIGHT_INPUT_CLASSES, 'placeholder': 'Last Name'}))
    selected_skills = forms.MultipleChoiceField(
        choices=UserProfile.SKILL_CATEGORIES,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input text-blue-600 bg-white border-gray-300 focus:ring-blue-500'}), # Tailored for checkboxes
        required=False
    )
    
    class Meta:
        model = UserProfile
        fields = ['phone', 'address', 'skills', 'selected_skills', 'experience_years', 'bio', 'profile_picture', 'upi_id', 'qr_code', 'bank_account_name', 'bank_account_number', 'bank_ifsc', 'bank_name']
        widgets = {
            'phone': forms.TextInput(attrs={'class': LIGHT_INPUT_CLASSES, 'placeholder': 'Phone Number'}),
            'address': forms.Textarea(attrs={'class': LIGHT_TEXTAREA_CLASSES, 'rows': 3, 'placeholder': 'Your Address'}),
            'skills': forms.Textarea(attrs={'class': LIGHT_TEXTAREA_CLASSES, 'rows': 3, 'placeholder': 'Enter additional skills (comma-separated)'}),
            'experience_years': forms.NumberInput(attrs={'class': LIGHT_INPUT_CLASSES, 'placeholder': 'Years of Experience'}),
            'bio': forms.Textarea(attrs={'class': LIGHT_TEXTAREA_CLASSES, 'rows': 4, 'placeholder': 'Tell us about yourself...'}),
            'profile_picture': forms.FileInput(attrs={
                'class': HIDDEN_FILE_INPUT_CLASSES, # Use custom hidden input for styling
                'accept': 'image/*',
                'data-max-size': '5242880',  # 5MB in bytes
                'onchange': 'previewImage(this)'
            }),
            'upi_id': forms.TextInput(attrs={'class': LIGHT_INPUT_CLASSES, 'placeholder': 'UPI ID'}),
            'qr_code': forms.FileInput(attrs={'class': HIDDEN_FILE_INPUT_CLASSES, 'accept': 'image/*'}), # Use custom hidden input for styling
            'bank_account_name': forms.TextInput(attrs={'class': LIGHT_INPUT_CLASSES, 'placeholder': 'Account holder name'}),
            'bank_account_number': forms.TextInput(attrs={'class': LIGHT_INPUT_CLASSES, 'placeholder': 'Account number'}),
            'bank_ifsc': forms.TextInput(attrs={'class': LIGHT_INPUT_CLASSES, 'placeholder': 'IFSC code'}),
            'bank_name': forms.TextInput(attrs={'class': LIGHT_INPUT_CLASSES, 'placeholder': 'Bank name'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Initialize user name fields from related User if instance is provided
        if getattr(self, 'instance', None) and getattr(self.instance, 'user', None):
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
        # Keep previously selected skills checked
        if getattr(self, 'instance', None) and getattr(self.instance, 'selected_skills', None):
            self.fields['selected_skills'].initial = list(self.instance.selected_skills or [])

    def clean_profile_picture(self):
        profile_picture = self.cleaned_data.get('profile_picture')
        
        if profile_picture and hasattr(profile_picture, 'content_type'):
            if profile_picture.size > 5 * 1024 * 1024:
                raise forms.ValidationError("Profile picture must be less than 5MB.")
            
            allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif']
            if profile_picture.content_type not in allowed_types:
                raise forms.ValidationError("Please upload a valid image file (JPG, PNG, or GIF).")
        
        return profile_picture

    def save(self, commit=True):
        # Save model fields normally, but ensure selected_skills from the form
        # is written back to the model JSONField so it persists and stays checked.
        obj = super().save(commit=False)
        obj.selected_skills = self.cleaned_data.get('selected_skills', [])
        if commit:
            obj.save()
            self.save_m2m()
        return obj

class RecruiterUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': LIGHT_INPUT_CLASSES, 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': LIGHT_INPUT_CLASSES, 'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'class': LIGHT_INPUT_CLASSES, 'placeholder': 'Email Address'}),
        }

class RecruiterProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['phone', 'address', 'profile_picture']
        widgets = {
            'phone': forms.TextInput(attrs={'class': LIGHT_INPUT_CLASSES, 'placeholder': 'Phone Number'}),
            'address': forms.Textarea(attrs={'class': LIGHT_TEXTAREA_CLASSES, 'rows': 3, 'placeholder': 'Your Address'}),
            'profile_picture': forms.FileInput(attrs={'class': HIDDEN_FILE_INPUT_CLASSES, 'accept': 'image/*'}), # Use custom hidden input for styling
        }

class WorkExampleForm(forms.ModelForm):
    class Meta:
        model = WorkExample
        fields = ['title', 'description', 'work_type', 'file']
        widgets = {
            'title': forms.TextInput(attrs={'class': LIGHT_INPUT_CLASSES, 'placeholder': 'Work Title'}),
            'description': forms.Textarea(attrs={'class': LIGHT_TEXTAREA_CLASSES, 'rows': 3, 'placeholder': 'Brief Description of Work'}),
            'work_type': forms.Select(attrs={'class': LIGHT_SELECT_CLASSES}),
            'file': forms.FileInput(attrs={'class': HIDDEN_FILE_INPUT_CLASSES, 'accept': '*/*'}), # Use custom hidden input for styling
        }

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['amount', 'payment_method']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': LIGHT_INPUT_CLASSES, 'step': '0.01', 'placeholder': 'Amount'}),
            'payment_method': forms.Select(attrs={'class': LIGHT_SELECT_CLASSES}),
        }

class WorkTrackingForm(forms.ModelForm):
    class Meta:
        model = WorkTracking
        fields = ['completion_notes', 'before_photos', 'after_photos', 'completion_video', 'work_files']
        widgets = {
            'completion_notes': forms.Textarea(attrs={
                'class': LIGHT_TEXTAREA_CLASSES, 
                'rows': 5,
                'placeholder': 'Describe the work completed, any challenges faced, and final results...'
            }),
            'before_photos': forms.FileInput(attrs={
                'class': HIDDEN_FILE_INPUT_CLASSES, # Use custom hidden input for styling
                'accept': 'image/*'
            }),
            'after_photos': forms.FileInput(attrs={
                'class': HIDDEN_FILE_INPUT_CLASSES, # Use custom hidden input for styling
                'accept': 'image/*'
            }),
            'completion_video': forms.FileInput(attrs={
                'class': HIDDEN_FILE_INPUT_CLASSES, # Use custom hidden input for styling
                'accept': 'video/*'
            }),
            'work_files': forms.FileInput(attrs={
                'class': HIDDEN_FILE_INPUT_CLASSES, # Use custom hidden input for styling
                'accept': '.pdf,.doc,.docx,.txt,.zip,.rar'
            }),
        }

class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['complaint_type', 'title', 'description', 'evidence_photos', 'evidence_videos', 'evidence_documents']
        widgets = {
            'complaint_type': forms.Select(attrs={'class': LIGHT_SELECT_CLASSES}),
            'title': forms.TextInput(attrs={
                'class': LIGHT_INPUT_CLASSES,
                'placeholder': 'Brief title for your complaint'
            }),
            'description': forms.Textarea(attrs={
                'class': LIGHT_TEXTAREA_CLASSES, 
                'rows': 6,
                'placeholder': 'Please provide detailed information about your complaint. Include dates, amounts, and any relevant details...'
            }),
            'evidence_photos': forms.FileInput(attrs={
                'class': HIDDEN_FILE_INPUT_CLASSES, # Use custom hidden input for styling
                'accept': 'image/*'
            }),
            'evidence_videos': forms.FileInput(attrs={
                'class': HIDDEN_FILE_INPUT_CLASSES, # Use custom hidden input for styling
                'accept': 'video/*'
            }),
            'evidence_documents': forms.FileInput(attrs={
                'class': HIDDEN_FILE_INPUT_CLASSES, # Use custom hidden input for styling
                'accept': '.pdf,.doc,.docx,.txt'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        user_type = kwargs.pop('user_type', None)
        super().__init__(*args, **kwargs)
        
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
        widget=forms.Select(attrs={'class': LIGHT_SELECT_CLASSES})
    )
    admin_notes = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': LIGHT_TEXTAREA_CLASSES, 
            'rows': 4,
            'placeholder': 'Admin notes about the resolution...'
        }),
        required=False
    )
    resolution_amount = forms.DecimalField(
        max_digits=10, 
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': LIGHT_INPUT_CLASSES, 'step': '0.01', 'placeholder': 'Resolution Amount'}),
        required=False,
        help_text="Required for partial payment resolution"
    )