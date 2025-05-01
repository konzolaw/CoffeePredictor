from django.contrib import admin
from django.urls import path, include
from coffee.views import download_report, send_feedback, prediction_results

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('coffee.urls')),
    path('download-report/', download_report, name='download_report'),
    path('send-feedback/', send_feedback, name='send_feedback'),
    path('results/', prediction_results, name='results'),
]
