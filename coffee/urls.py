from django.urls import path # type: ignore
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register_user, name='register'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('predictions/', views.predictions, name='predictions'),
    path('success/', views.success, name='success'),
    path('results/', views.prediction_results, name='prediction_results'),
    path('predict/', views.predict_yield, name='predict_yield'),
    path('save-farm-info/', views.save_farm_info, name='save_farm_info'),
    path('res/', views.submit_farm_info, name='submit_farm_info'),
    
]




