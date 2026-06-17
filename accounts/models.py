from django.db import models

class Beneficiary(models.Model):

    name = models.CharField(max_length=100)

    phone = models.CharField(max_length=15)

    email = models.EmailField()

    gender = models.CharField(max_length=20)

    district = models.CharField(max_length=100)

    education = models.CharField(max_length=100)

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