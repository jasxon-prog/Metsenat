"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from app.views import SponsorListCreateAPIView, SponsorDetailAPIView, StudentListCreateAPIView, StudentDetailAPIView, DashboardAPIView, StudentSponsorCreateAPIView, StudentSponsorUpdateAPIView, DashboardGraphAPIView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('sponsor/',SponsorListCreateAPIView.as_view()),
    path('sponsor/<int:pk>/', SponsorDetailAPIView.as_view()),
    path('sponsor-student/create/', StudentSponsorCreateAPIView.as_view()),
    path('sponsor-student/<int:pk>/', StudentSponsorUpdateAPIView.as_view()),
    path('student/', StudentListCreateAPIView.as_view()),
    path('student/<int:pk>/', StudentDetailAPIView.as_view()),
    path('dashboard/', DashboardAPIView.as_view()),
    path('dashboard/graph/', DashboardGraphAPIView.as_view()),
]