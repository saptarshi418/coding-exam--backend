# contests/models.py
from django.db import models
from django.conf import settings
# from django.contrib.auth.models import User


class Contest(models.Model):
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='contests')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    duration = models.IntegerField(help_text="Duration in minutes")
    start_time = models.DateTimeField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Question(models.Model):
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE, related_name='questions')
    title = models.CharField(max_length=255)
    description = models.TextField()
    marks = models.IntegerField()

    def __str__(self):
        return f"Question: {self.title} (Contest: {self.contest.title})"

class TestCase(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='test_cases')
    input = models.TextField()
    expected_output = models.TextField()

    def __str__(self):
        return f"TestCase for Question: {self.question.title}"
    




class Participation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    contest = models.ForeignKey(Contest, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)
    code_submission = models.TextField(blank=True, null=True)
    language = models.CharField(max_length=10, choices=[
        ('python', 'Python'),
        ('java', 'Java'),
        ('cpp', 'C++'),
        ('c', 'C'),
    ], blank=True, null=True)
    marks_obtained = models.FloatField(default=0.0)
    suspicious_count = models.IntegerField(default=0)
    ended_due_to_cheating = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'contest')

    def __str__(self):
        return f"{self.user.username} - {self.contest.title}"



class CodeSubmission(models.Model):
    participant = models.ForeignKey(Participation, on_delete=models.CASCADE)
    language = models.CharField(max_length=10, choices=[
        ('python', 'Python'),
        ('java', 'Java'),
        ('cpp', 'C++'),
        ('c', 'C')
    ])
    code = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    passed_all_tests = models.BooleanField(default=False)
    marks_awarded = models.IntegerField(default=0)

# class TestCase(models.Model):
#     contest = models.ForeignKey(Contest, on_delete=models.CASCADE, null=True, blank=True)

#     input_data = models.TextField()
#     expected_output = models.TextField()
#     marks = models.IntegerField(default=0)


class Submission(models.Model):
    participant = models.ForeignKey(Participation, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    code = models.TextField()
    language = models.CharField(max_length=20)
    submitted_at = models.DateTimeField(auto_now_add=True)
    passed_all_cases = models.BooleanField(default=False)
    score = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.participant.user.username} - {self.question.title} ({self.language})"
