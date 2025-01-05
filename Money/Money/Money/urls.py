"""
URL configuration for Money project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import path
from Crawler import views

urlpatterns = [
    path('', views.ViewEast().index, name='index'),
    path('line/', views.ViewEast().line, name='line'),
    path('bar/', views.ViewEast().bar, name='bar'),
    path('line_with_area/', views.ViewEast().line_with_area, name='line_with_area'),
    path('scatter/', views.ViewEast().scatter, name='scatter'),
    path('latest-update-time/', views.LatestTime.latest_update_time, name='latest_update_time'),
    path('export/csv/', views.ExportData().export_data_csv, name='export_csv'),
    path('export/pdf/', views.ExportData().export_data_pdf, name='export_pdf'),
]
