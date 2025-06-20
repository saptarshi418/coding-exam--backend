# # contests/views.py
# import subprocess

# from rest_framework import generics, permissions
# from .models import Contest, Question , Participation , TestCase , CodeSubmission , Submission
# from .serializers import ContestSerializer, QuestionSerializer , ParticipationDashboardSerializer
# from .permissions import IsOrganization , IsOwnerOrReadOnly 

# from rest_framework.permissions import IsAuthenticated 
# from django.utils import timezone
# from rest_framework.response import Response
# from rest_framework.decorators import api_view , permission_classes

# import tempfile
# from django.shortcuts import get_object_or_404

# from .utils import run_code


# # from rest_framework.decorators import api_view, permission_classes

# from rest_framework import status

# from .models import Contest, Question, CodeSubmission
# from .serializers import QuestionSerializer
# from .utils import run_code_safely





# class ContestCreateView(generics.CreateAPIView):
#     queryset = Contest.objects.all()
#     serializer_class = ContestSerializer
#     permission_classes = [IsAuthenticated, IsOrganization]

#     def perform_create(self, serializer):
#         serializer.save(created_by=self.request.user)


# class UpdateContestView(generics.RetrieveUpdateAPIView):
#     queryset = Contest.objects.all()
#     serializer_class = ContestSerializer
#     permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

# class DeleteContestView(generics.DestroyAPIView):
#     queryset = Contest.objects.all()
#     serializer_class = ContestSerializer
#     permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

# class QuestionDetailView(generics.RetrieveAPIView):
#     queryset = Question.objects.all()
#     serializer_class = QuestionSerializer
#     permission_classes = [permissions.IsAuthenticated]

# class QuestionUpdateView(generics.RetrieveUpdateAPIView):
#     queryset = Question.objects.all()
#     serializer_class = QuestionSerializer
#     permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

# class QuestionDeleteView(generics.DestroyAPIView):
#     queryset = Question.objects.all()
#     serializer_class = QuestionSerializer
#     permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]


# @api_view(['GET'])
# def list_contests(request):
#     now = timezone.now()

#     ongoing_contests = []
#     upcoming_contests = []

#     for contest in Contest.objects.all():
#         end_time = contest.start_time + timezone.timedelta(minutes=contest.duration)
#         if contest.start_time <= now <= end_time:
#             ongoing_contests.append(contest)
#         elif contest.start_time > now:
#             upcoming_contests.append(contest)

#     return Response({
#         "ongoing": ContestSerializer(ongoing_contests, many=True).data,
#         "upcoming": ContestSerializer(upcoming_contests, many=True).data,
#     })



# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def join_contest(request, contest_id):
#     user = request.user
#     try:
#         contest = Contest.objects.get(id=contest_id)
#     except Contest.DoesNotExist:
#         return Response({"error": "Contest not found"}, status=404)

#     now = timezone.now()
#     end_time = contest.start_time + timezone.timedelta(minutes=contest.duration)
#     if now < contest.start_time - timezone.timedelta(minutes=15):
#         return Response({"error": "Too early to join. Please come back within 15 minutes of the contest start time."}, status=400)
#     if now > end_time:
#         return Response({"error": "Contest has already ended."}, status=400)


#     # Ensure the user hasn't already joined
#     participation, created = Participation.objects.get_or_create(user=user, contest=contest)

#     return Response({
#         "message": "Contest joined successfully. Activate webcam and redirect to code editor.",
#         "contest_id": contest.id,
#         "language_options": ["python", "java", "cpp", "c"]
#     })



  






# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def test_code(request):
#     user = request.user
#     data = request.data
#     question_id = data.get("question_id")
#     code = data.get("code")
#     language = data.get("language")

#     try:
#         question = Question.objects.get(id=question_id)
#         test_cases = TestCase.objects.filter(question=question)
#     except Question.DoesNotExist:
#         return Response({"error": "Invalid question ID"}, status=400)

#     all_passed = True
#     results = []

#     for test_case in test_cases:
#         result, output = run_code(code, language, test_case.input_data)
#         expected = test_case.expected_output.strip()

#         passed = (output.strip() == expected)
#         results.append({
#             "input": test_case.input_data,
#             "expected": expected,
#             "output": output.strip(),
#             "passed": passed
#         })

#         if not passed:
#             all_passed = False

#     return Response({
#         "all_passed": all_passed,
#         "results": results
#     })




# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def report_violation(request, contest_id):
#     user = request.user
#     participation = get_object_or_404(Participation, user=user, contest_id=contest_id)

#     if participation.ended_due_to_cheating:
#         return Response({"message": "Exam already ended due to cheating"}, status=400)

#     participation.suspicious_count += 1
#     if participation.suspicious_count >= 4:
#         participation.ended_due_to_cheating = True
#     participation.save()

#     return Response({
#         "suspicious_count": participation.suspicious_count,
#         "ended_due_to_cheating": participation.ended_due_to_cheating
#     })



# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def contest_participants_dashboard(request, contest_id):
#     user = request.user
#     try:
#         contest = Contest.objects.get(id=contest_id, created_by=user)
#     except Contest.DoesNotExist:
#         return Response({"error": "Contest not found or access denied"}, status=404)

#     participations = Participation.objects.filter(contest=contest)
#     serializer = ParticipationDashboardSerializer(participations, many=True)

#     return Response({
#         "contest_name": contest.name,
#         "participants": serializer.data
#     })


# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def list_organization_contests(request):
#     user = request.user
#     contests = Contest.objects.filter(created_by=user)
#     data = [{"id": c.id, "name": c.name, "start_time": c.start_time} for c in contests]
#     return Response(data)


# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def check_contest_access(request, contest_id):
#     try:
#         contest = Contest.objects.get(id=contest_id)
#     except Contest.DoesNotExist:
#         return Response({"error": "Contest not found"}, status=404)

#     now = timezone.now()
#     start = contest.start_time
#     diff = (start - now).total_seconds()

#     if diff > 900:  # More than 15 minutes
#         return Response({"status": "too_early", "message": "Contest has not started yet. Come back closer to the start time."})
#     elif 0 < diff <= 900:  # Within 15 minutes
#         return Response({"status": "waiting", "seconds_remaining": int(diff)})
#     elif now >= start and now <= (start + timezone.timedelta(minutes=contest.duration)):
#         return Response({"status": "start", "message": "Contest has started. Redirect to code editor."})
#     else:
#         return Response({"status": "ended", "message": "Contest is over."})


# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def get_contest_questions(request, contest_id):
#     try:
#         contest = Contest.objects.get(id=contest_id)
#     except Contest.DoesNotExist:
#         return Response({'error': 'Contest not found.'}, status=status.HTTP_404_NOT_FOUND)

#     questions = Question.objects.filter(contest=contest)
#     serializer = QuestionSerializer(questions, many=True)
#     return Response(serializer.data, status=status.HTTP_200_OK)

# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def run_code(request, contest_id):
#     question_id = request.data.get('question_id')
#     language = request.data.get('language')
#     code = request.data.get('code')

#     try:
#         question = Question.objects.get(id=question_id, contest_id=contest_id)
#     except Question.DoesNotExist:
#         return Response({'error': 'Question not found.'}, status=status.HTTP_404_NOT_FOUND)

#     output = run_code_safely(code, language, question.test_input)
#     return Response({'output': output}, status=status.HTTP_200_OK)

# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def submit_code(request, contest_id):
#     question_id = request.data.get('question_id')
#     language = request.data.get('language')
#     code = request.data.get('code')

#     try:
#         question = Question.objects.get(id=question_id, contest_id=contest_id)
#     except Question.DoesNotExist:
#         return Response({'error': 'Question not found.'}, status=status.HTTP_404_NOT_FOUND)

#     try:
#         participation = Participation.objects.get(user=request.user, contest_id=contest_id)
#     except Participation.DoesNotExist:
#         return Response({'error': 'You have not joined this contest.'}, status=status.HTTP_403_FORBIDDEN)

#     # OPTIONAL: Check if code passes all test cases here
#     passed = False
#     marks = 0
#     output = run_code_safely(code, language, question.test_input)
#     if output.strip() == question.expected_output.strip():
#         passed = True
#         marks = question.marks if hasattr(question, 'marks') else 0

#     # Save submission
#     CodeSubmission.objects.create(
#         participant=participation,
#         language=language,
#         code=code,
#         passed_all_tests=passed,
#         marks_awarded=marks,
#     )

#     return Response({
#         'message': 'Submission saved.',
#         'passed_all_tests': passed,
#         'marks_awarded': marks
#     }, status=status.HTTP_201_CREATED)




#################################################

import subprocess
from rest_framework import generics, permissions, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.utils import timezone
from django.shortcuts import get_object_or_404
from rest_framework.generics import RetrieveAPIView

from .models import Contest, Question, Participation, TestCase , Submission
from .serializers import (
    ContestSerializer, 
    QuestionSerializer,
    ParticipationDashboardSerializer
)
from .permissions import IsOrganization, IsOwnerOrReadOnly
from .utils import run_code_safely


# --- Contest Management Views ---

class ContestCreateView(generics.CreateAPIView):
    queryset = Contest.objects.all()
    serializer_class = ContestSerializer
    permission_classes = [IsAuthenticated, IsOrganization]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class UpdateContestView(generics.RetrieveUpdateAPIView):
    queryset = Contest.objects.all()
    serializer_class = ContestSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]


class DeleteContestView(generics.DestroyAPIView):
    queryset = Contest.objects.all()
    serializer_class = ContestSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]


# --- Question Management Views ---

class QuestionDetailView(generics.RetrieveAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [IsAuthenticated]


class QuestionUpdateView(generics.RetrieveUpdateAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]


class QuestionDeleteView(generics.DestroyAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]


# --- Contest Listing ---

@api_view(['GET'])
def list_contests(request):
    now = timezone.now()
    ongoing = []
    upcoming = []

    for contest in Contest.objects.all():
        end_time = contest.start_time + timezone.timedelta(minutes=contest.duration)
        if contest.start_time <= now <= end_time:
            ongoing.append(contest)
        elif contest.start_time > now:
            upcoming.append(contest)

    return Response({
        "ongoing": ContestSerializer(ongoing, many=True).data,
        "upcoming": ContestSerializer(upcoming, many=True).data
    })


# --- Join Contest ---

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def join_contest(request, pk):
    user = request.user
    contest = get_object_or_404(Contest, id=pk)

    now = timezone.now()
    end_time = contest.start_time + timezone.timedelta(minutes=contest.duration)

    if now < contest.start_time - timezone.timedelta(minutes=15):
        return Response({"error": "Too early to join. Please come back within 15 minutes of the contest start time."}, status=400)
    if now > end_time:
        return Response({"error": "Contest has already ended."}, status=400)

    Participation.objects.get_or_create(user=user, contest=contest)

    return Response({
        "message": "Contest joined successfully. Activate webcam and redirect to code editor.",
        "contest_id": contest.id,
        "language_options": ["python", "java", "cpp", "c"]
    })


# --- Code Testing ---

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def test_code(request):
    user = request.user
    question_id = request.data.get("question_id")
    code = request.data.get("code")
    language = request.data.get("language")

    question = get_object_or_404(Question, id=question_id)
    test_cases = TestCase.objects.filter(question=question)

    all_passed = True
    results = []

    for case in test_cases:
        output = run_code_safely(code, language, case.input_data)
        expected = case.expected_output.strip()
        passed = (output.strip() == expected)
        results.append({
            "input": case.input_data,
            "expected": expected,
            "output": output.strip(),
            "passed": passed
        })
        if not passed:
            all_passed = False

    return Response({
        "all_passed": all_passed,
        "results": results
    })


# --- Report Cheating Violation ---

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def report_violation(request, contest_id):
    participation = get_object_or_404(Participation, user=request.user, contest_id=contest_id)

    if participation.ended_due_to_cheating:
        return Response({"message": "Exam already ended due to cheating"}, status=400)

    participation.suspicious_count += 1
    if participation.suspicious_count >= 4:
        participation.ended_due_to_cheating = True
    participation.save()

    return Response({
        "suspicious_count": participation.suspicious_count,
        "ended_due_to_cheating": participation.ended_due_to_cheating
    })


# --- Contest Dashboard for Owner ---

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def contest_participants_dashboard(request, contest_id):
    contest = get_object_or_404(Contest, id=contest_id, created_by=request.user)
    participations = Participation.objects.filter(contest=contest)
    serializer = ParticipationDashboardSerializer(participations, many=True)

    return Response({
        "contest_name": contest.name,
        "participants": serializer.data
    })


# --- List Contests by Organization ---

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_organization_contests(request):
    contests = Contest.objects.filter(created_by=request.user)
    data = [{"id": c.id, "name": c.name, "start_time": c.start_time} for c in contests]
    return Response(data)


# --- Check Contest Access for Participant ---

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_contest_access(request, contest_id):
    contest = get_object_or_404(Contest, id=contest_id)
    now = timezone.now()
    diff = (contest.start_time - now).total_seconds()

    if diff > 900:
        return Response({"status": "too_early", "message": "Contest has not started yet. Come back closer to the start time."})
    elif 0 < diff <= 900:
        return Response({"status": "waiting", "seconds_remaining": int(diff)})
    elif contest.start_time <= now <= (contest.start_time + timezone.timedelta(minutes=contest.duration)):
        return Response({"status": "start", "message": "Contest has started. Redirect to code editor."})
    else:
        return Response({"status": "ended", "message": "Contest is over."})


# --- Get Contest Questions ---

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_contest_questions(request, contest_id):
    contest = get_object_or_404(Contest, id=contest_id)
    questions = Question.objects.filter(contest=contest)
    serializer = QuestionSerializer(questions, many=True)
    return Response(serializer.data)


# --- Run Code for Specific Question ---

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def run_code(request, contest_id):
    question_id = request.data.get('question_id')
    language = request.data.get('language')
    code = request.data.get('code')

    question = get_object_or_404(Question, id=question_id, contest_id=contest_id)
    output = run_code_safely(code, language, question.test_input)
    return Response({'output': output})


# --- Submit Code for Grading ---

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from .models import Question, Participation, Submission
from .utils import run_code_safely  # Or wherever your helper is


from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.utils import timezone

from .models import Question, Participation, Submission


from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.utils import timezone

from .models import Question, Participation, Submission, TestCase


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_all_codes(request, contest_id):
    """
    Accepts submissions with passed_test_cases from frontend.
    Calculates score = passed_test_cases * 10.
    Saves to Submission table.
    """
    submissions = request.data.get('submissions', [])
    if not submissions:
        return Response({'error': 'No submissions provided.'}, status=status.HTTP_400_BAD_REQUEST)

    participation = get_object_or_404(Participation, user=request.user, contest_id=contest_id)
    results = []

    for item in submissions:
        question_id = item.get('question_id')
        language = item.get('language')
        code = item.get('code')
        passed_test_cases = item.get('passed_test_cases', 0)

        if not all([question_id, language, code]):
            continue  # skip incomplete

        question = get_object_or_404(Question, id=question_id, contest_id=contest_id)

        # ✅ Correct way: query TestCase directly
        total_cases = TestCase.objects.filter(question=question).count()
        passed_all_cases = passed_test_cases == total_cases

        score = passed_test_cases * 10

        # Save submission
        Submission.objects.create(
            participant=participation,
            question_id=question.id,
            code=code,
            language=language,
            submitted_at=timezone.now(),
            passed_all_cases=passed_all_cases,
            score=score
        )

        results.append({
            'question_id': question.id,
            'passed_test_cases': passed_test_cases,
            'total_test_cases': total_cases,
            'passed_all_cases': passed_all_cases,
            'score': score
        })

    return Response({
        'message': '✅ All submissions saved successfully.',
        'results': results
    }, status=status.HTTP_201_CREATED)


class RetrieveContestView(RetrieveAPIView):
    queryset = Contest.objects.all()
    serializer_class = ContestSerializer
    