from django.urls import path, include
from rest_framework_nested import routers
from surveys.views import SurveyView, QuestionView, SurveyQuestionView, QuestionOptionView, AnswerView, \
    ParticipantSurveyView, QuestionTypeView, SurveyDuplicateView, NotifyParticipantView

questions_router = routers.SimpleRouter()
questions_router.register(r'questions', QuestionView)

questions_options_router = routers.NestedSimpleRouter(questions_router, r'questions', lookup='question')
questions_options_router.register(r'options', QuestionOptionView)

questions_types_router = routers.SimpleRouter()
questions_types_router.register('question_types', QuestionTypeView)

surveys_router = routers.SimpleRouter()
surveys_router.register('surveys', SurveyView)

surveys_questions_router = routers.NestedSimpleRouter(surveys_router, 'surveys', lookup='survey')
surveys_questions_router.register('questions', SurveyQuestionView)

survey_duplicate_router = routers.SimpleRouter()
survey_duplicate_router.register('surveys', SurveyDuplicateView, basename="Duplicate survey")

survey_notify_router = routers.SimpleRouter()
survey_notify_router.register("surveys", NotifyParticipantView, basename="Notify survey")

surveys_questions_answers_router = routers.NestedSimpleRouter(surveys_questions_router, 'questions', lookup='question')
surveys_questions_answers_router.register('answers', AnswerView)

surveys_participants_router = routers.NestedSimpleRouter(surveys_router, 'surveys', lookup='survey')
surveys_participants_router.register('participants', ParticipantSurveyView)

urlpatterns = [
    path(r'', include(surveys_router.urls)),
    path(r'', include(questions_router.urls)),
    path(r'', include(surveys_questions_router.urls)),
    path(r'', include(surveys_participants_router.urls)),
    path(r'', include(questions_options_router.urls)),
    path(r'', include(questions_types_router.urls)),
    path(r'', include(surveys_questions_answers_router.urls)),
    path(r'', include(survey_duplicate_router.urls)),
    path(r'', include(survey_notify_router.urls)),
]
