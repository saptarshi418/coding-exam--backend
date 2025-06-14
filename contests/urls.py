# contests/urls.py
from django.urls import path
from . import views
from .views import (
    ContestCreateView, UpdateContestView, DeleteContestView,
    QuestionDetailView, QuestionUpdateView, QuestionDeleteView, join_contest, list_contests, submit_code, test_code , check_contest_access
)

urlpatterns = [
    path('', list_contests, name='list-contests'),

    path('create/', ContestCreateView.as_view(), name='create-contest'),
    path('<int:pk>/update/', UpdateContestView.as_view(), name='update-contest'),
    path('<int:pk>/delete/', DeleteContestView.as_view(), name='delete-contest'),

    path('questions/<int:pk>/', QuestionDetailView.as_view(), name='question-detail'),
    path('questions/<int:pk>/update/', QuestionUpdateView.as_view(), name='question-update'),
    path('questions/<int:pk>/delete/', QuestionDeleteView.as_view(), name='question-delete'),


    path('<int:contest_id>/check-access/', check_contest_access, name='check-contest-access'),

    path('<int:contest_id>/join/', join_contest, name='join-contest'),
    
    path('api/test/', test_code, name='test_code'),
    path('submit/', submit_code, name='submit_code'),
    path('<int:contest_id>/report_violation/', views.report_violation, name='report_violation'),



]
