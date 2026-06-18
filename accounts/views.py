from django.shortcuts import render
from .models import Beneficiary
from datetime import date
from .models import Beneficiary, AdmissionApplication
from django.shortcuts import render, redirect

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

from django.shortcuts import render, redirect

def admission_personal(request):


    if request.method == "POST":

        request.session['name'] = request.POST.get('name')
        request.session['phone'] = request.POST.get('phone')
        request.session['email'] = request.POST.get('email')
        request.session['gender'] = request.POST.get('gender')
        request.session['dob'] = request.POST.get('dob')
        request.session['address'] = request.POST.get('address')
        request.session['district'] = request.POST.get('district')
        request.session['category'] = request.POST.get('category')

        return redirect('admission_education')

    return render(request, 'accounts/admission_personal.html')



def admission_education(request):


    if request.method == "POST":

        request.session['college_name'] = request.POST.get('college_name')
        request.session['course_name'] = request.POST.get('course_name')
        request.session['academic_year'] = request.POST.get('academic_year')
        request.session['education_level'] = request.POST.get('education_level')

        return redirect('admission_support')

    return render(request, 'accounts/admission_education.html')



def admission_support(request):

    if request.method == "POST":

        request.session['support_required'] = request.POST.get('support_required')
        request.session['family_income'] = request.POST.get('family_income')
        request.session['reason'] = request.POST.get('reason')

        return redirect('admission_review')

    return render(request, 'accounts/admission_support.html')

def admission_review(request):

    data = {
    'name': request.session.get('name'),
    'phone': request.session.get('phone'),
    'email': request.session.get('email'),
    'district': request.session.get('district'),

    'college_name': request.session.get('college_name'),
    'course_name': request.session.get('course_name'),
    'academic_year': request.session.get('academic_year'),

    'support_required': request.session.get('support_required'),
    'family_income': request.session.get('family_income'),
}

    if request.method == "POST":
    
        beneficiary = Beneficiary.objects.create(
            name=request.session.get('name'),
            phone=request.session.get('phone'),
            email=request.session.get('email'),
            gender=request.session.get('gender'),
            district=request.session.get('district'),
            education=request.session.get('education_level'),
            date_of_birth=request.session.get('dob'),
            address=request.session.get('address'),
            category=request.session.get('category'),
            status='APPLIED'
        )
    
        AdmissionApplication.objects.create(
            beneficiary=beneficiary,
            college_name=request.session.get('college_name'),
            course_name=request.session.get('course_name'),
            academic_year=request.session.get('academic_year'),
            application_date=date.today(),
            support_required=request.session.get('support_required'),
            family_income=request.session.get('family_income'),
            reason=request.session.get('reason')
        )
        return redirect('home')
    
    return render(
        request,
        'accounts/admission_review.html',
        {'data': data} 
    )