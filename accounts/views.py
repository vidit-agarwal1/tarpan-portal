from django.shortcuts import render, redirect
from .models import Beneficiary, AdmissionApplication, DynamicField
from datetime import date
from django.db.models import Count
import random
import string
from .models import Beneficiary, AdmissionApplication, DynamicField, BeneficiaryDocument, AuditLog, FundingEntry, AdminAccount


# ─── Helpers ────────────────────────────────────────────────

def generate_applicant_id():
    """Generate a random unique username like TAR-A3X9K"""
    while True:
        suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
        candidate = f"TAR-{suffix}"
        if not Beneficiary.objects.filter(applicant_id=candidate).exists():
            return candidate
        
def admin_login_required(view_func):
    """Decorator to protect admin views."""
    def wrapper(request, *args, **kwargs):
        if not request.session.get('admin_logged_in'):
            return redirect('admin_login')
        return view_func(request, *args, **kwargs)
    return wrapper


# ─── Public pages ────────────────────────────────────────────

def home(request):
    return render(request, 'accounts/home.html')


# User login flow 

def user_login(request):
    error = None

    if request.method == "POST":
        login_id  = request.POST.get('applicant_id', '').strip()
        dob_input = request.POST.get('dob', '').strip()

        beneficiary = None

        # Try applicant_id first
        try:
            beneficiary = Beneficiary.objects.get(applicant_id=login_id)
        except Beneficiary.DoesNotExist:
            pass

        # Try enrollment_id second
        if beneficiary is None:
            try:
                beneficiary = Beneficiary.objects.get(enrollment_id=login_id)
            except Beneficiary.DoesNotExist:
                pass

        # Try email third
        if beneficiary is None:
            try:
                beneficiary = Beneficiary.objects.get(email=login_id)
            except Beneficiary.DoesNotExist:
                pass
            except Beneficiary.MultipleObjectsReturned:
                # Two applicants with same email — fall back to ID login
                error = "Multiple accounts found with this email. Please log in with your Applicant ID instead."
                return render(request, 'accounts/user_login.html', {'error': error})

        if beneficiary is None:
            error = "Invalid ID, email, or Date of Birth."
            return render(request, 'accounts/user_login.html', {'error': error})

        if str(beneficiary.date_of_birth) == dob_input:
            request.session['logged_in_applicant_id'] = beneficiary.applicant_id
            return redirect('user_dashboard')
        else:
            error = "Invalid ID, email, or Date of Birth."

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
    funding_entries = FundingEntry.objects.filter(beneficiary=beneficiary)
    total_funding = sum(e.amount for e in funding_entries)

    context = {
        'beneficiary': beneficiary,
        'application': application,
        'documents' : documents,
        'total_funding' : total_funding,
    }

    return render(request, 'accounts/user_dashboard.html', context)


#Admin views
@admin_login_required
def admin_dashboard(request):
    from django.db.models import Sum

    total_funding = FundingEntry.objects.aggregate(
        total=Sum('amount')
    )['total'] or 0

    context = {
        'total_beneficiaries': Beneficiary.objects.count(),
        'applied_count':  Beneficiary.objects.filter(status='APPLIED').count(),
        'verified_count': Beneficiary.objects.filter(status='VERIFIED').count(),
        'enrolled_count': Beneficiary.objects.filter(status='ENROLLED').count(),
        'total_funding':  total_funding,
        'admin_username': request.session.get('admin_username'),
    }
    return render(request, 'accounts/admin_dashboard.html', context)

@admin_login_required
def admission_applications(request):
    context = {'applications': Beneficiary.objects.filter(status='APPLIED')}
    return render(request, 'accounts/admission_applications.html', context)

@admin_login_required
def verified_applications(request):
    context = {'applications': Beneficiary.objects.filter(status='VERIFIED')}
    return render(request, 'accounts/verified_applications.html', context)

@admin_login_required
def enrolled_beneficiaries(request):
    context = {'beneficiaries': Beneficiary.objects.filter(status='ENROLLED')}
    return render(request, 'accounts/enrolled_beneficiaries.html', context)


@admin_login_required
def verify_application(request, beneficiary_id):
    beneficiary = Beneficiary.objects.get(id=beneficiary_id)
    beneficiary.status = 'VERIFIED'
    beneficiary.save()

    # audit logs
    AuditLog.objects.create(
        beneficiary=beneficiary,
        action='VERIFY',
        description=f"Application for {beneficiary.name} was verified.",
        performed_by = request.session.get('admin_username')
    )

    return redirect('admission_applications')

@admin_login_required
def enroll_beneficiary(request, beneficiary_id):
    beneficiary = Beneficiary.objects.get(id=beneficiary_id)
    beneficiary.status = 'ENROLLED'
    beneficiary.enrollment_id = "TP2026" + str(beneficiary.id).zfill(3)
    beneficiary.save()

    # audit logs
    AuditLog.objects.create(
        beneficiary=beneficiary,
        action='ENROLL',
        description=f"{beneficiary.name} was enrolled. Enrollment ID: {beneficiary.enrollment_id}.",
        performed_by = request.session.get('admin_username')
    )

    return redirect('verified_applications')

@admin_login_required
def beneficiary_detail(request, beneficiary_id):
    beneficiary = Beneficiary.objects.get(id=beneficiary_id)
    application = AdmissionApplication.objects.get(beneficiary=beneficiary)
    documents   = BeneficiaryDocument.objects.filter(beneficiary=beneficiary)
    funding_entries = FundingEntry.objects.filter(beneficiary=beneficiary)
    total_funding = sum(e.amount for e in funding_entries)

    context = {
        'beneficiary': beneficiary,
        'application': application,
        'documents': documents,
        'funding_entries' : funding_entries,
        'total_funding' : total_funding,
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

        # Bank details
        request.session['bank_account_number']          = request.POST.get('bank_account_number')
        request.session['bank_ifsc_code']               = request.POST.get('bank_ifsc_code', '').upper()
        request.session['bank_name']                    = request.POST.get('bank_name')
        request.session['bank_branch_name']             = request.POST.get('bank_branch_name')
        request.session['bank_account_holder_relation'] = request.POST.get('bank_account_holder_relation')
        request.session['bank_notes']                   = request.POST.get('bank_notes')


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

        # Bank details
        'bank_account_number':          request.session.get('bank_account_number'),
        'bank_ifsc_code':               request.session.get('bank_ifsc_code'),
        'bank_name':                    request.session.get('bank_name'),
        'bank_branch_name':             request.session.get('bank_branch_name'),
        'bank_account_holder_relation': request.session.get('bank_account_holder_relation'),
        'bank_notes':                   request.session.get('bank_notes'),
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

            # Bank details
            bank_account_number=request.session.get('bank_account_number'),
            bank_ifsc_code=request.session.get('bank_ifsc_code'),
            bank_name=request.session.get('bank_name'),
            bank_branch_name=request.session.get('bank_branch_name'),
            bank_account_holder_relation=request.session.get('bank_account_holder_relation'),
            bank_notes=request.session.get('bank_notes'),
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
@admin_login_required
def edit_beneficiary(request, beneficiary_id):
    beneficiary = Beneficiary.objects.get(id=beneficiary_id)
    application = AdmissionApplication.objects.get(beneficiary=beneficiary)

    if request.method == "POST":

        # capturing old values for the audit log
        old_status = beneficiary.status
        old_name = beneficiary.name

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

        # Build a useful description for the audit logs
        changes = []
        if old_name != beneficiary.name:
            changes.append(f"name changed from '{old_name}' to '{beneficiary.name}'")
        if old_status != beneficiary.status:
            changes.append(f"status changed from '{old_status}' to '{beneficiary.status}'")
        if not changes:
            changes.append("profile details updated")

        AuditLog.objects.create(
            beneficiary=beneficiary,
            action='EDIT',
            description=f"Profile edited for {beneficiary.name}: {', '.join(changes)}.",
            performed_by = request.session.get('admin_username'),
        )

        return redirect('beneficiary_detail', beneficiary_id=beneficiary.id)

    context = {
        'beneficiary': beneficiary,
        'application': application,
        'status_choices': Beneficiary.STATUS_CHOICES,
    }
    return render(request, 'accounts/edit_beneficiary.html', context)


# Admin: Upload document to beneficiary profile
@admin_login_required
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

            AuditLog.objects.create(
                beneficiary=beneficiary,
                action='DOC_UPLOAD',
                description=f"Document '{title}' uploaded for {beneficiary.name}.",
                performed_by = request.session.get('admin_username')
            )

    return redirect('beneficiary_detail', beneficiary_id=beneficiary.id)


#Admin: Delete document
@admin_login_required
def delete_document(request, document_id):
    doc = BeneficiaryDocument.objects.get(id=document_id)
    beneficiary_id = doc.beneficiary.id

    AuditLog.objects.create(
        beneficiary_id = beneficiary_id,
        action='DOC_DELETE',
        description=f"Document '{doc.title}' deleted from {beneficiary_id.name}'s profile.",
        performed_by = request.session.get('admin_username')
    )

    doc.file.delete()  # removes the actual file from disk
    doc.delete()
    return redirect('beneficiary_detail', beneficiary_id=beneficiary_id)

@admin_login_required
def audit_logs(request):
    logs = AuditLog.objects.select_related('beneficiary').all()

    # Filter by beneficiary name if searched
    search = request.GET.get('search', '').strip()
    if search:
        logs = logs.filter(beneficiary__name__icontains=search)

    # Filter by action type if selected
    action_filter = request.GET.get('action', '').strip()
    if action_filter:
        logs = logs.filter(action=action_filter)

    context = {
        'logs': logs,
        'search': search,
        'action_filter': action_filter,
        'action_choices': AuditLog.ACTION_CHOICES,
    }
    return render(request, 'accounts/audit_logs.html', context)

# ─── Admin: Add funding entry ─────────────────────────────────
@admin_login_required
def add_funding(request, beneficiary_id):
    beneficiary = Beneficiary.objects.get(id=beneficiary_id)

    if request.method == "POST":
        purpose = request.POST.get('purpose', '').strip()
        amount  = request.POST.get('amount', '').strip()
        date_input = request.POST.get('date', '').strip()
        note    = request.POST.get('note', '').strip()

        if purpose and amount and date_input:
            entry = FundingEntry.objects.create(
                beneficiary=beneficiary,
                purpose=purpose,
                amount=amount,
                date=date_input,
                note=note or None,
            )

            AuditLog.objects.create(
                beneficiary=beneficiary,
                action='FUNDING',
                description=f"Funding entry added for {beneficiary.name}: ₹{amount} for {purpose} on {date_input}.",
                performed_by = request.session.get('admin_username')
            )

    return redirect('beneficiary_detail', beneficiary_id=beneficiary_id)


# ─── Admin: Delete funding entry ──────────────────────────────
@admin_login_required
def delete_funding(request, entry_id):
    entry = FundingEntry.objects.get(id=entry_id)
    beneficiary = entry.beneficiary

    AuditLog.objects.create(
        beneficiary=beneficiary,
        action='FUNDING',
        description=f"Funding entry deleted for {beneficiary.name}: ₹{entry.amount} for {entry.purpose} on {entry.date}.",
        performed_by = request.session.get('admin_username')
    )

    entry.delete()
    return redirect('beneficiary_detail', beneficiary_id=beneficiary.id)

# Expenditure and grants monitoring
@admin_login_required
def expenditure(request):
    from django.db.models import Sum

    all_entries = FundingEntry.objects.select_related('beneficiary').all()

    total_funding  = all_entries.aggregate(total=Sum('amount'))['total'] or 0
    total_entries  = all_entries.count()
    unique_purposes = all_entries.values('purpose').distinct().count()
    funded_count   = all_entries.values('beneficiary').distinct().count()

    # Total per beneficiary
    beneficiary_ids = all_entries.values_list('beneficiary', flat=True).distinct()
    beneficiary_totals = []
    for bid in beneficiary_ids:
        beneficiary = Beneficiary.objects.get(id=bid)
        total = all_entries.filter(beneficiary=beneficiary).aggregate(
            total=Sum('amount')
        )['total'] or 0
        beneficiary_totals.append({'beneficiary': beneficiary, 'total': total})

    beneficiary_totals.sort(key=lambda x: x['total'], reverse=True)

    # Total per purpose
    purpose_totals = []
    for purpose in all_entries.values_list('purpose', flat=True).distinct():
        total = all_entries.filter(purpose=purpose).aggregate(
            total=Sum('amount')
        )['total'] or 0
        purpose_totals.append({'purpose': purpose, 'total': total})

    purpose_totals.sort(key=lambda x: x['total'], reverse=True)

    context = {
        'all_entries':        all_entries,
        'total_funding':      total_funding,
        'total_entries':      total_entries,
        'unique_purposes':    unique_purposes,
        'funded_count':       funded_count,
        'beneficiary_totals': beneficiary_totals,
        'purpose_totals':     purpose_totals,
    }
    return render(request, 'accounts/expenditure.html', context)

# ─── Admin login ─────────────────────────────────────────────

def admin_login(request):
    error = None

    if request.method == "POST":
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        try:
            admin = AdminAccount.objects.get(username=username)
            if admin.check_password(password):
                request.session['admin_logged_in'] = True
                request.session['admin_username']  = admin.username
                return redirect('admin_dashboard')
            else:
                error = "Invalid username or password."
        except AdminAccount.DoesNotExist:
            error = "Invalid username or password."

    return render(request, 'accounts/admin_login.html', {'error': error})


def admin_logout(request):
    request.session.pop('admin_logged_in', None)
    request.session.pop('admin_username', None)
    return redirect('admin_login')