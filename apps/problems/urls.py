from django.urls import path 
from . import views 

urlpatterns = [
    path('', views.problem_list, name='problem_list'),
    path("<int:problem_id>/run-sql/", views.run_sql_submission, name="run_sql_submission"),
    path('<slug:slug>/', views.problem_detail, name='problem_detail'),
]