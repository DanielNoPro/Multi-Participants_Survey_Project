from django.contrib import admin

from surveys.models import ParticipantSurvey, Question, QuestionType, Survey

# Register your models here.
admin.site.register(QuestionType)
admin.site.register(Survey)
admin.site.register(Question)
admin.site.register(ParticipantSurvey)
