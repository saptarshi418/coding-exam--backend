# # contests/urls.py
# from django.urls import path
# from . import views
# from .views import (
#     ContestCreateView, UpdateContestView, DeleteContestView,
#     QuestionDetailView, QuestionUpdateView, QuestionDeleteView, join_contest, list_contests, submit_code, test_code , check_contest_access
# )

# urlpatterns = [
#     path('', list_contests, name='list-contests'),

#     path('create/', ContestCreateView.as_view(), name='create-contest'),
#     path('<int:pk>/update/', UpdateContestView.as_view(), name='update-contest'),
#     path('<int:pk>/delete/', DeleteContestView.as_view(), name='delete-contest'),

#     path('questions/<int:pk>/', QuestionDetailView.as_view(), name='question-detail'),
#     path('questions/<int:pk>/update/', QuestionUpdateView.as_view(), name='question-update'),
#     path('questions/<int:pk>/delete/', QuestionDeleteView.as_view(), name='question-delete'),


#     path('<int:contest_id>/check-access/', check_contest_access, name='check-contest-access'),

#     path('<int:contest_id>/join/', join_contest, name='join-contest'),
    
#     path('api/test/', test_code, name='test_code'),
#     path('submit/', submit_code, name='submit_code'),
#     path('<int:contest_id>/report_violation/', views.report_violation, name='report_violation'),
#     path('<int:contest_id>/questions/', views.get_contest_questions, name='get_contest_questions'),
#     path('<int:contest_id>/run/', views.run_code, name='run_code'),
#     path('<int:contest_id>/submit/', views.submit_code, name='submit_code'),



# ]


#############################################################


from django.urls import path
from .views import (
    ContestCreateView, UpdateContestView, DeleteContestView,
    QuestionDetailView, QuestionUpdateView, QuestionDeleteView, RetrieveContestView, 
    list_contests, join_contest, check_contest_access,
    get_contest_questions, run_code, submit_code, report_violation,
    test_code, contest_participants_dashboard, list_organization_contests,
)

urlpatterns = [
    # ✅ Contest list and creation
    path('', list_contests, name='list-contests'),
    path('create/', ContestCreateView.as_view(), name='create-contest'),
    path('<int:pk>/update/', UpdateContestView.as_view(), name='update-contest'),
    path('<int:pk>/delete/', DeleteContestView.as_view(), name='delete-contest'),

    # ✅ Question detail & management
    path('questions/<int:pk>/', QuestionDetailView.as_view(), name='question-detail'),
    path('questions/<int:pk>/update/', QuestionUpdateView.as_view(), name='question-update'),
    path('questions/<int:pk>/delete/', QuestionDeleteView.as_view(), name='question-delete'),

    # ✅ Join, check access, view dashboard
    path('<int:contest_id>/check-access/', check_contest_access, name='check-contest-access'),
    path('<int:pk>/join/', join_contest, name='join-contest'),
    path('<int:contest_id>/participants/', contest_participants_dashboard, name='contest-participants-dashboard'),

    # ✅ Contest organization list
    path('my-contests/', list_organization_contests, name='list-organization-contests'),

    # ✅ Get questions for a contest
    path('<int:contest_id>/questions/', get_contest_questions, name='get-contest-questions'),

    # ✅ Run, submit, test code — use clear REST style
    path('<int:contest_id>/run/', run_code, name='run-code'),
    path('<int:contest_id>/submit/', submit_code, name='submit-code'),
    path('<int:contest_id>/report-violation/', report_violation, name='report-violation'),

    # ✅ Generic code testing endpoint
    path('test/', test_code, name='test-code'),

    path('contests/<int:pk>/', RetrieveContestView.as_view(), name='contest-detail'),
]
