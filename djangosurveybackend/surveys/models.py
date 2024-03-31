import logging

from django.conf import settings
from django.db import models
from django.utils.module_loading import import_string

from surveys.constants import LogicalOperator, MathematicalOperator


class QuestionType(models.Model):
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Question Types"  # show in the admin

    def __str__(self):
        return self.name


class Question(models.Model):
    question_type = models.ForeignKey(
        QuestionType, on_delete=models.CASCADE, related_name="question_type"
    )
    content = models.TextField(blank=False)
    is_active = models.BooleanField(default=True)
    is_editable = models.BooleanField(default=True)
    is_deletable = models.BooleanField(default=True)
    question_created_by = models.ForeignKey(
        import_string(settings.AUTH_USER_MODEL_MODULE),
        on_delete=models.CASCADE,
        related_name="question_created_by",
    )
    question_created_at = models.DateTimeField(auto_now_add=True)
    question_updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Questions"  # show in the admin
        ordering = ("-question_created_at",)

    def __str__(self):
        return self.content


class Survey(models.Model):
    title = models.CharField(max_length=255)
    questions = models.ManyToManyField(Question, through="SurveyQuestion")
    participant = models.ManyToManyField(
        import_string(settings.AUTH_USER_MODEL_MODULE), through="ParticipantSurvey"
    )
    description = models.TextField(blank=True)
    start_date = models.DateTimeField(auto_now_add=False)
    end_date = models.DateTimeField(auto_now=False)
    is_active = models.BooleanField(default=True)
    survey_created_at = models.DateTimeField(auto_now_add=True)
    survey_updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Surveys"  # show in the admin
        ordering = ("-survey_created_at",)

    def __str__(self):
        return self.title


class ParticipantSurvey(models.Model):
    class Meta:
        verbose_name_plural = "Participant Surveys"  # show in the admin
        unique_together = (("participant", "survey"),)
        ordering = ("-participant_joined_at",)

    participant = models.ForeignKey(
        import_string(settings.AUTH_USER_MODEL_MODULE), on_delete=models.CASCADE
    )
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    status = models.CharField(max_length=55)
    is_active = models.BooleanField(default=True)
    invited_participant_at = models.DateTimeField(auto_now_add=True)
    participant_joined_at = models.DateTimeField(auto_now=True)


class SurveyQuestionSet(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    set_created_by = models.ForeignKey(
        import_string(settings.AUTH_USER_MODEL_MODULE),
        on_delete=models.CASCADE,
        related_name="set_created_by",
    )
    set_created_at = models.DateTimeField(auto_now_add=True)
    set_updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Question Sets"  # show in the admin
        ordering = ("-set_created_at",)

    def __str__(self):
        return self.survey


class SurveyQuestion(models.Model):
    class Meta:
        unique_together = (("question", "survey", "asked_by"),)
        ordering = ("-asked_at",)

    set = models.ForeignKey(SurveyQuestionSet, on_delete=models.CASCADE)
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    question_order = models.PositiveIntegerField(default=1)
    asked_by = models.ForeignKey(
        import_string(settings.AUTH_USER_MODEL_MODULE), on_delete=models.CASCADE
    )
    asked_at = models.DateTimeField(auto_now_add=True)
    adjusted_at = models.DateTimeField(auto_now=True)
    order = models.PositiveIntegerField(
        default=0,
        blank=False,
        null=False,
    )


class SurveyQuestionCondition(models.Model):
    class Meta:
        ordering = ("-condition_created_at", "-condition_updated_at")

    set = models.ForeignKey(SurveyQuestionSet, on_delete=models.CASCADE)
    logical_operator = models.CharField(max_length=50, choices=LogicalOperator.choices)
    survey_question = models.ForeignKey(SurveyQuestion, on_delete=models.CASCADE)
    value = models.TextField(null=True, blank=True)
    operator = models.CharField(max_length=50, choices=MathematicalOperator.choices)
    is_active = models.BooleanField(default=True)
    condition_created_by = models.ForeignKey(
        import_string(settings.AUTH_USER_MODEL_MODULE),
        on_delete=models.CASCADE,
        related_name="condition_created_by",
    )
    condition_created_at = models.DateTimeField(auto_now_add=True)
    condition_updated_at = models.DateTimeField(auto_now=True)

    def check_condition(self, value):
        try:
            if self.operator == MathematicalOperator.MATH_OPERATOR_EQUAL:
                return self.value == value
            elif self.operator == MathematicalOperator.MATH_OPERATOR_GREATER_THAN:
                return float(self.value) > float(value)
            elif self.operator == MathematicalOperator.MATH_OPERATOR_LESS_THAN:
                return float(self.value) < float(value)
            elif (
                self.operator
                == MathematicalOperator.MATH_OPERATOR_GREATER_THAN_OR_EQUAL
            ):
                return float(self.value) >= float(value)
            elif self.operator == MathematicalOperator.MATH_OPERATOR_LESS_THAN_OR_EQUAL:
                return float(self.value) <= float(value)
            elif self.operator == MathematicalOperator.MATH_OPERATOR_IN:
                if isinstance(value, list):
                    return self.value in value
            elif self.operator == MathematicalOperator.MATH_OPERATOR_NOT_IN:
                if isinstance(value, list):
                    return self.value not in value
        except Exception as e:
            logging.error(e)
        return False


class QuestionOption(models.Model):
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="options"
    )
    content = models.TextField(blank=False)
    is_active = models.BooleanField(default=True)
    option_created_at = models.DateTimeField(auto_now_add=True)
    option_updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "QuestionOptions"  # show in the admin
        ordering = ("-option_created_at",)

    def __str__(self):
        return self.content


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    option = models.ForeignKey(
        QuestionOption, on_delete=models.SET_NULL, blank=True, null=True
    )
    content = models.TextField(blank=False, null=True)
    answered_by = models.ForeignKey(
        import_string(settings.AUTH_USER_MODEL_MODULE), on_delete=models.CASCADE
    )
    answered_at = models.DateTimeField(auto_now_add=True)
    answer_updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (
            ("question", "survey", "option", "answered_by", "answered_at"),
        )
        ordering = ("-answered_at",)

    def __str__(self):
        return self.content


class SurveySubmit(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    submitted_by = models.ForeignKey(
        import_string(settings.AUTH_USER_MODEL_MODULE), on_delete=models.CASCADE
    )
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (("survey", "submitted_by", "submitted_at"),)
        ordering = ("-submitted_at",)

    def __str__(self):
        return f"{str(self.submitted_by)}_{str(self.survey)}_{str(self.submitted_at)}"
