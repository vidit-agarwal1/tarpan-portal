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

]