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

    STATUS_CHOICES = [
        ('ENQUIRY', 'Enquiry'),
        ('APPLIED', 'Admission Applied'),
        ('VERIFIED', 'Verified'),
        ('ENROLLED', 'Enrolled'),
        ('ACADEMIC', 'Academic Monitoring'),
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