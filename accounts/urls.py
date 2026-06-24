from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('user-dashboard/', views.user_dashboard, name='user_dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admission-applications/', views.admission_applications, name='admission_applications'),
    path('verified-applications/', views.verified_applications, name='verified_applications'),
    path('enrolled-beneficiaries/', views.enrolled_beneficiaries, name='enrolled-beneficiaries'),


path(
    'admission-applications/',
    views.admission_applications,
    name='admission_applications'
),

path(
    'verified-applications/',
    views.verified_applications,
    name='verified_applications'
),

path(
    'enrolled-beneficiaries/',
    views.enrolled_beneficiaries,
    name='enrolled_beneficiaries'
),

path(
    'verify-application/<int:beneficiary_id>/',
    views.verify_application,
    name='verify_application'
),

path(
    'enroll-beneficiary/<int:beneficiary_id>/',
    views.enroll_beneficiary,
    name='enroll_beneficiary'
),

path(
    'beneficiary/<int:beneficiary_id>/',
    views.beneficiary_detail,
    name='beneficiary_detail'
),

path(
'academic-monitoring/',
views.academic_monitoring,
name='academic_monitoring'
),

path(
    'academic-update/<int:beneficiary_id>/',
    views.academic_update,
    name='academic_update'
),

path(
'expenditure-monitoring/',
views.expenditure_monitoring,
name='expenditure_monitoring'
),

path(
    'financial-update/<int:beneficiary_id>/',
    views.financial_update,
    name='financial_update'
),


path('admission/personal/', views.admission_personal, name='admission_personal'),
path('admission/education/', views.admission_education, name='admission_education'),
path('admission/support/', views.admission_support, name='admission_support'),
path('admission/review/', views.admission_review, name='admission_review'),


]