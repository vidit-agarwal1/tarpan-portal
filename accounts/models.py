from django.db import models

class Beneficiary(models.Model):

    name = models.CharField(max_length=100)

    phone = models.CharField(max_length=15)

    email = models.EmailField()

    gender = models.CharField(max_length=20)

    district = models.CharField(max_length=100)

    education = models.CharField(max_length=100)

    date_of_birth = models.DateField(
        blank=True,
        null=True
    )

    address = models.TextField(
        blank=True,
        null=True
    )

    category = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    enrollment_id = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    applicant_id = models.CharField(
        max_length=20,
        blank = True,
        null = True,
        unique = True
    )

    STATUS_CHOICES = [
        ('ENQUIRY', 'Enquiry'),
        ('APPLIED', 'Admission Applied'),
        ('VERIFIED', 'Verified'),
        ('ENROLLED', 'Enrolled'),
        ('JOB', 'Job Assistance'),
        ('COMPLETED', 'Completed'),
    ]

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='ENQUIRY'
    )

    def __str__(self):
        return self.name

class AdmissionApplication(models.Model):

    beneficiary = models.OneToOneField(
        Beneficiary,
        on_delete=models.CASCADE
    )

    family_income = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True
    )

    reason = models.TextField(
        blank=True,
        null=True
    )

    college_name = models.CharField(max_length=200)

    course_name = models.CharField(max_length=200)

    academic_year = models.CharField(max_length=50)

    application_date = models.DateField()

    support_required = models.TextField()

    approved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.beneficiary.name} - {self.course_name}"
    
# Add this below your AdmissionApplication model

class DynamicField(models.Model):
    application = models.ForeignKey(
        'AdmissionApplication',
        on_delete=models.CASCADE,
        related_name='dynamic_fields'
    )
    field_name  = models.CharField(max_length=100)
    field_value = models.TextField()  # stores sentences, words, numbers — all as text

    def __str__(self):
        return f"{self.field_name}: {self.field_value}"
    
class BeneficiaryDocument(models.Model):
    beneficiary = models.ForeignKey(
        Beneficiary,
        on_delete = models.CASCADE,
        related_name= 'documents'
    )
    title = models.CharField(max_length = 200)
    file = models.FileField(upload_to='beneficiary_documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.beneficiary.name} - {self.title}"   

class AuditLog(models.Model):

    ACTION_CHOICES = [
        ('VERIFY', 'Application Verified'),
        ('ENROLL', 'Beneficiary Enrolled'),
        ('EDIT', 'Profile Edited'),
        ('DOC_UPLOAD', 'Document Uploaded'),
        ('DOC_DELETE', 'Document Deleted'),
        ('FUNDING', 'Funding Entry Added')
    ]

    beneficiary = models.ForeignKey(
        Beneficiary,
        on_delete=models.SET_NULL,
        null=True,
        related_name='audit_logs'
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.timestamp} - {self.action} - {self.beneficiary}"

    class Meta:
        ordering = ['-timestamp']  # newest first

# Funding entry class   
class FundingEntry(models.Model):
    beneficiary = models.ForeignKey(
        Beneficiary,
        on_delete=models.CASCADE,
        related_name='funding_entries'
    )
    purpose = models.CharField(max_length=200)  # e.g. Food, Rent, Travel
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.beneficiary.name} - {self.purpose} - ₹{self.amount}"

    class Meta:
        ordering = ['-date']