from django.contrib import admin

from surveys.models import QuestionType, Survey, ParticipantSurvey, Question

# Register your models here.
admin.site.register(QuestionType)
admin.site.register(Survey)
admin.site.register(Question)
admin.site.register(ParticipantSurvey)
