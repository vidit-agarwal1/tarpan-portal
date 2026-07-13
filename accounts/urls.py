from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    # User login
    path('user-login/', views.user_login, name='user_login'),
    path('user-logout/', views.user_logout, name='user_logout'),
    path('user-dashboard/', views.user_dashboard, name='user_dashboard'),

    # Admin
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admission-applications/', views.admission_applications, name='admission_applications'),
    path('verified-applications/', views.verified_applications, name='verified_applications'),
    path('enrolled-beneficiaries/', views.enrolled_beneficiaries, name='enrolled_beneficiaries'),
    path('verify-application/<int:beneficiary_id>/', views.verify_application, name='verify_application'),
    path('enroll-beneficiary/<int:beneficiary_id>/', views.enroll_beneficiary, name='enroll_beneficiary'),
    path('beneficiary/<int:beneficiary_id>/', views.beneficiary_detail, name='beneficiary_detail'),
    path('beneficiary/<int:beneficiary_id>/edit/', views.edit_beneficiary, name='edit_beneficiary'),
    path('beneficiary/<int:beneficiary_id>/upload-document/', views.upload_document, name='upload_document'),
    path('beneficiary/<int:beneficiary_id>/add-funding/', views.add_funding, name='add_funding'),
    path('document/<int:document_id>/delete/', views.delete_document, name='delete_document'),
    path('funding/<int:entry_id>/delete/', views.delete_funding, name='delete_funding'),
    path('audit-logs/', views.audit_logs, name='audit_logs'),

    # Admission form steps
    path('admission/personal/', views.admission_personal, name='admission_personal'),
    path('admission/education/', views.admission_education, name='admission_education'),
    path('admission/support/', views.admission_support, name='admission_support'),
    path('admission/review/', views.admission_review, name='admission_review'),
    path('admission/submitted/', views.application_submitted, name='application_submitted'),
]