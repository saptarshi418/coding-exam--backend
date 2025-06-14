# contests/views.py
import subprocess

from rest_framework import generics, permissions
from .models import Contest, Question , Participation , TestCase , CodeSubmission , Submission
from .serializers import ContestSerializer, QuestionSerializer , ParticipationDashboardSerializer
from .permissions import IsOrganization , IsOwnerOrReadOnly 

from rest_framework.permissions import IsAuthenticated 
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.decorators import api_view , permission_classes

import tempfile
from django.shortcuts import get_object_or_404

from .utils import run_code






class ContestCreateView(generics.CreateAPIView):
    queryset = Contest.objects.all()
    serializer_class = ContestSerializer
    permission_classes = [IsAuthenticated, IsOrganization]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class UpdateContestView(generics.RetrieveUpdateAPIView):
    queryset = Contest.objects.all()
    serializer_class = ContestSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

class DeleteContestView(generics.DestroyAPIView):
    queryset = Contest.objects.all()
    serializer_class = ContestSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

class QuestionDetailView(generics.RetrieveAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticated]

class QuestionUpdateView(generics.RetrieveUpdateAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

class QuestionDeleteView(generics.DestroyAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]


@api_view(['GET'])
def list_contests(request):
    now = timezone.now()

    ongoing_contests = []
    upcoming_contests = []

    for contest in Contest.objects.all():
        end_time = contest.start_time + timezone.timedelta(minutes=contest.duration)
        if contest.start_time <= now <= end_time:
            ongoing_contests.append(contest)
        elif contest.start_time > now:
            upcoming_contests.append(contest)

    return Response({
        "ongoing": ContestSerializer(ongoing_contests, many=True).data,
        "upcoming": ContestSerializer(upcoming_contests, many=True).data,
    })



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def join_contest(request, contest_id):
    user = request.user
    try:
        contest = Contest.objects.get(id=contest_id)
    except Contest.DoesNotExist:
        return Response({"error": "Contest not found"}, status=404)

    now = timezone.now()
    end_time = contest.start_time + timezone.timedelta(minutes=contest.duration)
    if now < contest.start_time - timezone.timedelta(minutes=15):
        return Response({"error": "Too early to join. Please come back within 15 minutes of the contest start time."}, status=400)
    if now > end_time:
        return Response({"error": "Contest has already ended."}, status=400)


    # Ensure the user hasn't already joined
    participation, created = Participation.objects.get_or_create(user=user, contest=contest)

    return Response({
        "message": "Contest joined successfully. Activate webcam and redirect to code editor.",
        "contest_id": contest.id,
        "language_options": ["python", "java", "cpp", "c"]
    })



  




@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_code(request, contest_id):
    user = request.user
    code = request.data.get('code')
    language = request.data.get('language')

    if not code or not language:
        return Response({"error": "Code and language are required"}, status=400)

    participation = get_object_or_404(Participation, user=user, contest_id=contest_id)
    test_cases = TestCase.objects.filter(contest_id=contest_id)

    all_passed = True
    total_marks = 0

    for case in test_cases:
        passed, output = run_code(code, language, case.input_data)
        expected = case.expected_output.strip()

        if output.strip() != expected:
            all_passed = False
        else:
            total_marks += case.marks

    CodeSubmission.objects.create(
        participant=participation,
        language=language,
        code=code,
        passed_all_tests=all_passed,
        marks_awarded=total_marks
    )

    return Response({
        "message": "✅ All test cases passed" if all_passed else "❌ Not all test cases passed",
        "marks": total_marks
    })


# import subprocess
# import tempfile
# from rest_framework.decorators import api_view, permission_classes
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.response import Response


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def test_code(request):
    user = request.user
    data = request.data
    question_id = data.get("question_id")
    code = data.get("code")
    language = data.get("language")

    try:
        question = Question.objects.get(id=question_id)
        test_cases = TestCase.objects.filter(question=question)
    except Question.DoesNotExist:
        return Response({"error": "Invalid question ID"}, status=400)

    all_passed = True
    results = []

    for test_case in test_cases:
        result, output = run_code(code, language, test_case.input_data)
        expected = test_case.expected_output.strip()

        passed = (output.strip() == expected)
        results.append({
            "input": test_case.input_data,
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



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_code(request, contest_id):
    user = request.user
    code = request.data.get('code')
    language = request.data.get('language')

    if not code or not language:
        return Response({"error": "Code and language are required"}, status=400)

    participation = get_object_or_404(Participation, user=user, contest_id=contest_id)
    test_cases = TestCase.objects.filter(contest_id=contest_id)

    all_passed = True
    total_marks = 0

    for case in test_cases:
        passed, output = run_code(code, language, case.input_data)
        expected = case.expected_output.strip()

        if output.strip() != expected:
            all_passed = False
        else:
            total_marks += case.marks

    CodeSubmission.objects.create(
        participant=participation,
        language=language,
        code=code,
        passed_all_tests=all_passed,
        marks_awarded=total_marks
    )

    return Response({
        "message": "✅ All test cases passed" if all_passed else "❌ Not all test cases passed",
        "marks": total_marks
    })



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def report_violation(request, contest_id):
    user = request.user
    participation = get_object_or_404(Participation, user=user, contest_id=contest_id)

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



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def contest_participants_dashboard(request, contest_id):
    user = request.user
    try:
        contest = Contest.objects.get(id=contest_id, created_by=user)
    except Contest.DoesNotExist:
        return Response({"error": "Contest not found or access denied"}, status=404)

    participations = Participation.objects.filter(contest=contest)
    serializer = ParticipationDashboardSerializer(participations, many=True)

    return Response({
        "contest_name": contest.name,
        "participants": serializer.data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_organization_contests(request):
    user = request.user
    contests = Contest.objects.filter(created_by=user)
    data = [{"id": c.id, "name": c.name, "start_time": c.start_time} for c in contests]
    return Response(data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_contest_access(request, contest_id):
    try:
        contest = Contest.objects.get(id=contest_id)
    except Contest.DoesNotExist:
        return Response({"error": "Contest not found"}, status=404)

    now = timezone.now()
    start = contest.start_time
    diff = (start - now).total_seconds()

    if diff > 900:  # More than 15 minutes
        return Response({"status": "too_early", "message": "Contest has not started yet. Come back closer to the start time."})
    elif 0 < diff <= 900:  # Within 15 minutes
        return Response({"status": "waiting", "seconds_remaining": int(diff)})
    elif now >= start and now <= (start + timezone.timedelta(minutes=contest.duration)):
        return Response({"status": "start", "message": "Contest has started. Redirect to code editor."})
    else:
        return Response({"status": "ended", "message": "Contest is over."})
