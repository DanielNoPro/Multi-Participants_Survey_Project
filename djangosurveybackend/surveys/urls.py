from django.urls import include, path
from rest_framework_nested import routers

from surveys.views import (
    AnswerView,
    NotifyParticipantView,
    ObtainSurveyAuthTokenFromCallbackRedirectToken,
    ObtainTenantEmailCallbackToken,
    ParticipantSurveyView,
    QuestionOptionView,
    QuestionTypeView,
    QuestionView,
    SubmitSurveyView,
    SurveyAnswerStatisticView,
    SurveyDuplicateView,
    SurveyQuestionView,
    SurveyView,
    ActivateParticipantSurveyView,
    DeactivateParticipantSurveyView,
    SurveySubmitView,
    SurveyQuestionSetView,
    SurveyQuestionConditionView,
    NextSetSurveyView,
)

questions_router = routers.SimpleRouter()
questions_router.register(r"questions", QuestionView)

questions_options_router = routers.NestedSimpleRouter(
    questions_router, r"questions", lookup="question"
)
questions_options_router.register(r"options", QuestionOptionView)

questions_types_router = routers.SimpleRouter()
questions_types_router.register("question_types", QuestionTypeView)

surveys_router = routers.SimpleRouter()
surveys_router.register("surveys", SurveyView)

surveys_questions_set_router = routers.NestedSimpleRouter(
    surveys_router, "surveys", lookup="survey"
)
surveys_questions_set_router.register("sets", SurveyQuestionSetView)

surveys_questions_router = routers.NestedSimpleRouter(
    surveys_questions_set_router, "sets", lookup="set"
)
surveys_questions_router.register("questions", SurveyQuestionView)

surveys_questions_condition_router = routers.NestedSimpleRouter(
    surveys_questions_set_router, "sets", lookup="set"
)
surveys_questions_condition_router.register("condition", SurveyQuestionConditionView)

surveys_submits_router = routers.NestedSimpleRouter(
    surveys_router, "surveys", lookup="survey"
)
surveys_submits_router.register("submits", SurveySubmitView)

survey_duplicate_router = routers.SimpleRouter()
survey_duplicate_router.register(
    "surveys", SurveyDuplicateView, basename="Duplicate survey"
)

survey_notify_router = routers.SimpleRouter()
survey_notify_router.register(
    "surveys", NotifyParticipantView, basename="Notify survey"
)

survey_submit_router = routers.SimpleRouter()
survey_submit_router.register("surveys", SubmitSurveyView, basename="Submit survey")

survey_questions_set_next_router = routers.NestedSimpleRouter(
    surveys_questions_set_router, "sets", lookup="set"
)
survey_questions_set_next_router.register(
    "surveys", NextSetSurveyView, basename="Next set survey"
)

surveys_questions_answers_router = routers.NestedSimpleRouter(
    surveys_questions_router, "questions", lookup="question"
)
surveys_questions_answers_router.register("answers", AnswerView)

surveys_questions_option_router = routers.NestedSimpleRouter(
    surveys_questions_router, "questions", lookup="question"
)
surveys_questions_option_router.register("options", QuestionOptionView)

surveys_participants_router = routers.NestedSimpleRouter(
    surveys_router, "surveys", lookup="survey"
)
surveys_participants_router.register("participants", ParticipantSurveyView)

activate_surveys_participants_router = routers.SimpleRouter()
activate_surveys_participants_router.register(
    "participants", ActivateParticipantSurveyView, basename="Activate participant"
)

deactivate_surveys_participants_router = routers.SimpleRouter()
deactivate_surveys_participants_router.register(
    "participants", DeactivateParticipantSurveyView, basename="Deactivate participant"
)

surveys_statistics_router = routers.SimpleRouter()
surveys_statistics_router.register(
    "surveys", SurveyAnswerStatisticView, basename="Statistics survey"
)

urlpatterns = [
    path(r"", include(surveys_router.urls)),
    path(r"", include(questions_router.urls)),
    path(r"", include(surveys_questions_set_router.urls)),
    path(r"", include(surveys_questions_router.urls)),
    path(r"", include(surveys_questions_condition_router.urls)),
    path(r"", include(surveys_submits_router.urls)),
    path(r"", include(surveys_participants_router.urls)),
    path(r"", include(activate_surveys_participants_router.urls)),
    path(r"", include(deactivate_surveys_participants_router.urls)),
    path(r"", include(questions_options_router.urls)),
    path(r"", include(questions_types_router.urls)),
    path(r"", include(surveys_questions_answers_router.urls)),
    path(r"", include(survey_duplicate_router.urls)),
    path(r"", include(survey_notify_router.urls)),
    path(r"", include(survey_submit_router.urls)),
    path(r"", include(survey_questions_set_next_router.urls)),
    path(r"", include(surveys_statistics_router.urls)),
    path("token/redirect", ObtainSurveyAuthTokenFromCallbackRedirectToken.as_view()),
    path("survey/email", ObtainTenantEmailCallbackToken.as_view(), name="auth_survey"),
]
