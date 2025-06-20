#contests/serializers.py

from rest_framework import serializers
from .models import Contest, Question, TestCase , Participation


class TestCaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestCase
        fields = ['id', 'input', 'expected_output']


class QuestionSerializer(serializers.ModelSerializer):
    test_cases = TestCaseSerializer(many=True)

    class Meta:
        model = Question
        fields = ['id', 'title', 'description', 'marks', 'test_cases']

    def update(self, instance, validated_data):
        test_cases_data = validated_data.pop('test_cases', [])

        # Update basic fields
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.save()

        # Update test cases (delete and recreate or match by id)
        instance.test_cases.all().delete()
        for test_case_data in test_cases_data:
            TestCase.objects.create(question=instance, **test_case_data)

        return instance


class ContestSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True)
    start_time = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%SZ")  # Ensure 'Z' for UTC


    class Meta:
        model = Contest
        fields = ['id', 'title', 'description', 'duration', 'start_time', 'questions']

    def create(self, validated_data):
        questions_data = validated_data.pop('questions')
        user = self.context['request'].user

        if user.user_type != 'organization':
            raise serializers.ValidationError("Only organization users can create contests.")

        # Remove created_by if somehow present in validated_data
        validated_data.pop('created_by', None)

        try:
            contest = Contest.objects.create(**validated_data, created_by=user)

            for question_data in questions_data:
                test_cases_data = question_data.pop('test_cases', [])
                question = Question.objects.create(contest=contest, **question_data)
                for test_case_data in test_cases_data:
                    TestCase.objects.create(question=question, **test_case_data)

            return contest
        except Exception as e:
            raise serializers.ValidationError(f"Error creating contest: {str(e)}")


    def update(self, instance, validated_data):
        questions_data = validated_data.pop('questions', [])

        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.duration = validated_data.get('duration', instance.duration)
        instance.start_time = validated_data.get('start_time', instance.start_time)
        instance.save()

        existing_question_ids = [q.id for q in instance.questions.all()]
        incoming_question_ids = [q.get('id') for q in questions_data if 'id' in q]

        # Delete removed questions
        for q_id in existing_question_ids:
            if q_id not in incoming_question_ids:
                Question.objects.filter(id=q_id).delete()

        for question_data in questions_data:
            test_cases_data = question_data.pop('test_cases', [])
            q_id = question_data.get('id', None)

            if q_id:  # update existing
                question = Question.objects.get(id=q_id, contest=instance)
                question.title = question_data.get('title', question.title)
                question.description = question_data.get('description', question.description)
                question.marks = question_data.get('marks', question.marks)
                question.save()

                existing_tc_ids = [tc.id for tc in question.test_cases.all()]
                incoming_tc_ids = [tc.get('id') for tc in test_cases_data if 'id' in tc]

                # Delete removed test cases
                for tc_id in existing_tc_ids:
                    if tc_id not in incoming_tc_ids:
                        TestCase.objects.filter(id=tc_id).delete()

                for test_case_data in test_cases_data:
                    tc_id = test_case_data.get('id', None)
                    if tc_id:
                        test_case = TestCase.objects.get(id=tc_id, question=question)
                        test_case.input = test_case_data.get('input', test_case.input)
                        test_case.expected_output = test_case_data.get('expected_output', test_case.expected_output)
                        test_case.save()
                    else:
                        TestCase.objects.create(question=question, **test_case_data)
            else:  # create new question
                question = Question.objects.create(contest=instance, **question_data)
                for test_case_data in test_cases_data:
                    TestCase.objects.create(question=question, **test_case_data)

        return instance



class ParticipationDashboardSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')

    class Meta:
        model = Participation
        fields = [
            'username',
            'code_submission',
            'language',
            'marks_obtained',
            'suspicious_count',
            'ended_due_to_cheating',
            'joined_at',
        ]