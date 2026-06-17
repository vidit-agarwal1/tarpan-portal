from django.shortcuts import render
from .models import Beneficiary

def home(request):
    return render(request, 'accounts/home.html')

def user_dashboard(request):
    return render(request, 'accounts/user_dashboard.html')

def admin_dashboard(request):

    total_beneficiaries = Beneficiary.objects.count()

    context = {
        'total_beneficiaries': total_beneficiaries
    }

    return render(
        request,
        'accounts/admin_dashboard.html',
        context
    )
def admission_applications(request):

    applications = Beneficiary.objects.filter(
        status='APPLIED'
    )

    context = {
        'applications': applications
    }

    return render(
        request,
        'accounts/admission_applications.html',
        context
    )

def verified_applications(request):

    applications = Beneficiary.objects.filter(
        status='VERIFIED'
    )

    context = {
        'applications': applications
    }

    return render(
        request,
        'accounts/verified_applications.html',
        context
    )

def enrolled_beneficiaries(request):

    beneficiaries = Beneficiary.objects.filter(
        status='ENROLLED'
    )

    context = {
        'beneficiaries': beneficiaries
    }

    return render(
        request,
        'accounts/enrolled_beneficiaries.html',
        context
    )