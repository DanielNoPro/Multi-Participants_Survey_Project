from django.contrib.auth.models import User
from django.db import models


class QuestionType(models.Model):
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'QuestionTypes'  # show in the admin

    def __str__(self):
        return self.name


class Question(models.Model):
    question_type = models.ForeignKey(QuestionType, on_delete=models.CASCADE, related_name='question_type')
    content = models.TextField(blank=False)
    is_active = models.BooleanField(default=True)
    question_created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='question_created_by')
    question_created_at = models.DateTimeField(auto_now_add=True)
    question_updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Questions'  # show in the admin
        ordering = ('-question_created_at',)

    def __str__(self):
        return self.content


class QuestionOption(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')
    content = models.TextField(blank=False)
    is_active = models.BooleanField(default=True)
    option_created_at = models.DateTimeField(auto_now_add=True)
    option_updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'QuestionOptions'  # show in the admin
        ordering = ('-option_created_at',)

    def __str__(self):
        return self.content


class Survey(models.Model):
    title = models.CharField(max_length=255)
    questions = models.ManyToManyField(Question, through="SurveyQuestion")
    participant = models.ManyToManyField(User, through="ParticipantSurvey")
    description = models.TextField(blank=True)
    start_date = models.DateTimeField(auto_now_add=False)
    end_date = models.DateTimeField(auto_now=False)
    is_active = models.BooleanField(default=True)
    survey_created_at = models.DateTimeField(auto_now_add=True)
    survey_updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Surveys'  # show in the admin
        ordering = ('-survey_created_at',)

    def __str__(self):
        return self.title


class ParticipantSurvey(models.Model):
    class Meta:
        unique_together = (('participant', 'survey'),)
        ordering = ('-participant_joined_at',)

    participant = models.ForeignKey(User, on_delete=models.CASCADE)
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    status = models.CharField(max_length=55)
    is_active = models.BooleanField(default=True)
    invited_participant_at = models.DateTimeField(auto_now_add=True)
    participant_joined_at = models.DateTimeField(auto_now=True)


class SurveyQuestion(models.Model):

    class Meta:
        unique_together = (('question', 'survey', 'asked_by'),)
        ordering = ('-asked_at',)

    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    asked_by = models.ForeignKey(User, on_delete=models.CASCADE)
    asked_at = models.DateTimeField(auto_now_add=True)
    adjusted_at = models.DateTimeField(auto_now=True)


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    option = models.ForeignKey(QuestionOption, on_delete=models.SET_NULL, blank=True, null=True)
    content = models.TextField(blank=False, null=True)
    answered_by = models.ForeignKey(User, on_delete=models.CASCADE)
    answered_at = models.DateTimeField(auto_now_add=True)
    answer_updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (('question', 'survey', 'option', 'answered_by'),)
        ordering = ('-answered_at',)

    def __str__(self):
        return self.content
