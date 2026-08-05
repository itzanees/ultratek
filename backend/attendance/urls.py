from django.urls import path
from .import views

urlpatterns = [
    path('', views.home, name='attendance_home'),
    path('/mark', views.mark_site_attendance, name='mark_attendance'),
    path('ajax/load-project-crew/', views.crew_list_ajax, name='crew_list_ajax'),
    # path()
]