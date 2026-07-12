from django.shortcuts import render, redirect
from .models import Beneficiary, AdmissionApplication, DynamicField
from datetime import date
from django.db.models import Count
import random
import string
from .models import Beneficiary, AdmissionApplication, DynamicField, BeneficiaryDocument


# ─── Helpers ────────────────────────────────────────────────

def generate_applicant_id():
    """Generate a random unique username like TAR-A3X9K"""
    while True:
        suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
        candidate = f"TAR-{suffix}"
        if not Beneficiary.objects.filter(applicant_id=candidate).exists():
            return candidate


# ─── Public pages ────────────────────────────────────────────

def home(request):
    return render(request, 'accounts/home.html')


# ─── User login flow ─────────────────────────────────────────

def user_login(request):
    error = None

    if request.method == "POST":
        applicant_id = request.POST.get('applicant_id', '').strip()
        dob_input    = request.POST.get('dob', '').strip()

        try:
            beneficiary = Beneficiary.objects.get(applicant_id=applicant_id)
        except Beneficiary.DoesNotExist:
            error = "Invalid Applicant ID or Date of Birth."
            return render(request, 'accounts/user_login.html', {'error': error})

        if str(beneficiary.date_of_birth) == dob_input:
            request.session['logged_in_applicant_id'] = beneficiary.applicant_id
            return redirect('user_dashboard')
        else:
            error = "Invalid Applicant ID or Date of Birth."

    return render(request, 'accounts/user_login.html', {'error': error})


def user_logout(request):
    request.session.pop('logged_in_applicant_id', None)
    return redirect('user_login')


def user_dashboard(request):
    applicant_id = request.session.get('logged_in_applicant_id')

    if not applicant_id:
        return redirect('user_login')

    beneficiary = Beneficiary.objects.get(applicant_id=applicant_id)
    application = AdmissionApplication.objects.filter(
        beneficiary=beneficiary
    ).first()
    documents = BeneficiaryDocument.objects.filter(beneficiary=beneficiary)

    context = {
        'beneficiary': beneficiary,
        'application': application,
        'documents' : documents,
    }

    return render(request, 'accounts/user_dashboard.html', context)


#Admin views

def admin_dashboard(request):
    context = {
        'total_beneficiaries': Beneficiary.objects.count(),
        'applied_count':  Beneficiary.objects.filter(status='APPLIED').count(),
        'verified_count': Beneficiary.objects.filter(status='VERIFIED').count(),
        'enrolled_count': Beneficiary.objects.filter(status='ENROLLED').count(),
    }
    return render(request, 'accounts/admin_dashboard.html', context)


def admission_applications(request):
    context = {'applications': Beneficiary.objects.filter(status='APPLIED')}
    return render(request, 'accounts/admission_applications.html', context)


def verified_applications(request):
    context = {'applications': Beneficiary.objects.filter(status='VERIFIED')}
    return render(request, 'accounts/verified_applications.html', context)


def enrolled_beneficiaries(request):
    context = {'beneficiaries': Beneficiary.objects.filter(status='ENROLLED')}
    return render(request, 'accounts/enrolled_beneficiaries.html', context)


def verify_application(request, beneficiary_id):
    beneficiary = Beneficiary.objects.get(id=beneficiary_id)
    beneficiary.status = 'VERIFIED'
    beneficiary.save()
    return redirect('admission_applications')


def enroll_beneficiary(request, beneficiary_id):
    beneficiary = Beneficiary.objects.get(id=beneficiary_id)
    beneficiary.status = 'ENROLLED'
    beneficiary.enrollment_id = "TP2026" + str(beneficiary.id).zfill(3)
    beneficiary.save()
    return redirect('verified_applications')


def beneficiary_detail(request, beneficiary_id):
    beneficiary = Beneficiary.objects.get(id=beneficiary_id)
    application = AdmissionApplication.objects.get(beneficiary=beneficiary)
    documents   = BeneficiaryDocument.objects.filter(beneficiary=beneficiary)
    context = {
        'beneficiary': beneficiary,
        'application': application,
        'documents': documents,
    }
    return render(request, 'accounts/beneficiary_detail.html', context)


# Admission multi-step form

def admission_personal(request):
    if request.method == "POST":
        request.session['name']     = request.POST.get('name')
        request.session['phone']    = request.POST.get('phone')
        request.session['email']    = request.POST.get('email')
        request.session['gender']   = request.POST.get('gender')
        request.session['dob']      = request.POST.get('dob')
        request.session['address']  = request.POST.get('address')
        request.session['district'] = request.POST.get('district')
        request.session['category'] = request.POST.get('category')
        return redirect('admission_education')
    return render(request, 'accounts/admission_personal.html')


def admission_education(request):
    if request.method == "POST":
        request.session['college_name']   = request.POST.get('college_name')
        request.session['course_name']    = request.POST.get('course_name')
        request.session['academic_year']  = request.POST.get('academic_year')
        request.session['education_level'] = request.POST.get('education_level')
        return redirect('admission_support')
    return render(request, 'accounts/admission_education.html')


def admission_support(request):
    if request.method == "POST":
        request.session['support_required'] = request.POST.get('support_required')
        request.session['family_income']     = request.POST.get('family_income')
        request.session['reason']            = request.POST.get('reason')

        field_names  = request.POST.getlist('field_names[]')
        field_values = request.POST.getlist('field_values[]')

        dynamic_fields = []
        for name, value in zip(field_names, field_values):
            name  = name.strip()
            value = value.strip()
            if name:
                dynamic_fields.append({'name': name, 'value': value})

        request.session['dynamic_fields'] = dynamic_fields
        return redirect('admission_review')
    return render(request, 'accounts/admission_support.html')


def admission_review(request):
    data = {
        'name':             request.session.get('name'),
        'phone':            request.session.get('phone'),
        'email':            request.session.get('email'),
        'district':         request.session.get('district'),
        'college_name':     request.session.get('college_name'),
        'course_name':      request.session.get('course_name'),
        'academic_year':    request.session.get('academic_year'),
        'support_required': request.session.get('support_required'),
        'family_income':    request.session.get('family_income'),
        'dynamic_fields':   request.session.get('dynamic_fields', []),
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
            status='APPLIED',
            applicant_id=generate_applicant_id(),  # ← generated here
        )

        application = AdmissionApplication.objects.create(
            beneficiary=beneficiary,
            college_name=request.session.get('college_name'),
            course_name=request.session.get('course_name'),
            academic_year=request.session.get('academic_year'),
            application_date=date.today(),
            support_required=request.session.get('support_required'),
            family_income=request.session.get('family_income'),
            reason=request.session.get('reason'),
        )

        for field in request.session.get('dynamic_fields', []):
            DynamicField.objects.create(
                application=application,
                field_name=field['name'],
                field_value=field['value'],
            )

        # Store the new ID in session so we can show it on confirmation
        request.session['new_applicant_id'] = beneficiary.applicant_id
        return redirect('application_submitted')

    return render(request, 'accounts/admission_review.html', {'data': data})


def application_submitted(request):
    applicant_id = request.session.pop('new_applicant_id', None)
    return render(
        request,
        'accounts/application_submitted.html',
        {'applicant_id': applicant_id}
    )

# Admin: Edit beneficiary profile

def edit_beneficiary(request, beneficiary_id):
    beneficiary = Beneficiary.objects.get(id=beneficiary_id)
    application = AdmissionApplication.objects.get(beneficiary=beneficiary)

    if request.method == "POST":
        # Personal details
        beneficiary.name         = request.POST.get('name')
        beneficiary.phone        = request.POST.get('phone')
        beneficiary.email        = request.POST.get('email')
        beneficiary.gender       = request.POST.get('gender')
        beneficiary.date_of_birth = request.POST.get('dob') or None
        beneficiary.address      = request.POST.get('address')
        beneficiary.district     = request.POST.get('district')
        beneficiary.category     = request.POST.get('category')
        beneficiary.status       = request.POST.get('status')
        beneficiary.enrollment_id = request.POST.get('enrollment_id')
        beneficiary.save()

        # Application details
        application.college_name     = request.POST.get('college_name')
        application.course_name      = request.POST.get('course_name')
        application.academic_year    = request.POST.get('academic_year')
        application.support_required = request.POST.get('support_required')
        application.family_income    = request.POST.get('family_income') or None
        application.reason           = request.POST.get('reason')
        application.save()

        return redirect('beneficiary_detail', beneficiary_id=beneficiary.id)

    context = {
        'beneficiary': beneficiary,
        'application': application,
        'status_choices': Beneficiary.STATUS_CHOICES,
    }
    return render(request, 'accounts/edit_beneficiary.html', context)


# Admin: Upload document to beneficiary profile

def upload_document(request, beneficiary_id):
    beneficiary = Beneficiary.objects.get(id=beneficiary_id)

    if request.method == "POST":
        title = request.POST.get('title', '').strip()
        file  = request.FILES.get('file')

        if title and file:
            BeneficiaryDocument.objects.create(
                beneficiary=beneficiary,
                title=title,
                file=file,
            )

    return redirect('beneficiary_detail', beneficiary_id=beneficiary.id)


#Admin: Delete document

def delete_document(request, document_id):
    doc = BeneficiaryDocument.objects.get(id=document_id)
    beneficiary_id = doc.beneficiary.id
    doc.file.delete()  # removes the actual file from disk
    doc.delete()
    return redirect('beneficiary_detail', beneficiary_id=beneficiary_id)