import logging

from dependency_injector.wiring import inject, Provide
from django.contrib.auth.models import User, Group
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.db import transaction
from django.http import HttpResponse, JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.vary import vary_on_headers
from rest_framework import viewsets, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes, permission_classes, action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.backends import TokenBackend

from surveybackend import Container, settings
from surveybackend.services import MailService
from surveys.models import Question, QuestionOption, Survey, Answer, SurveyQuestion, ParticipantSurvey, QuestionType
from surveys.serializers import QuestionSerializer, QuestionOptionSerializer, SurveySerializer, AnswerSerializer, \
    SurveyQuestionSerializer, PartitionSurveySerializer, QuestionTypeSerializer, UserSerializer, GroupSerializer

CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)


# Create your views here.
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
class UserView(viewsets.ModelViewSet):
    lookup_field = 'id'
    queryset = User.objects.all()
    serializer_class = UserSerializer


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
class GroupView(viewsets.ModelViewSet):
    lookup_field = 'id'
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
class QuestionTypeView(viewsets.ModelViewSet):
    lookup_field = 'id'
    queryset = QuestionType.objects.all()
    serializer_class = QuestionTypeSerializer

    @method_decorator(cache_page(CACHE_TTL))
    @method_decorator(vary_on_headers("Authorization"))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @method_decorator(cache_page(CACHE_TTL))
    @method_decorator(vary_on_headers("Authorization"))
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
class QuestionView(viewsets.ModelViewSet):
    lookup_field = 'id'
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
class QuestionOptionView(viewsets.ModelViewSet):
    lookup_field = 'id'
    queryset = QuestionOption.objects.all()
    serializer_class = QuestionOptionSerializer

    def get_queryset(self):
        return QuestionOption.objects.filter(question_id=self.kwargs['question_id'])


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
class SurveyView(viewsets.ModelViewSet):
    lookup_field = 'id'
    queryset = Survey.objects.all()
    serializer_class = SurveySerializer


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
class NotifyParticipantView(viewsets.ViewSet):
    serializer_class = UserSerializer
    model_class = Survey

    @csrf_exempt
    @transaction.atomic
    @action(detail=True, methods=['post'], url_name='notify')
    @inject
    def notify(
            self, request, pk: int,
            mail_service: MailService = Provide[Container.mail_service],
            subject: str = Provide[Container.config.SURVEY_SUBJECT],
            template: str = Provide[Container.config.SURVEY_TEMPLATE],
    ):
        token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
        try:
            valid_data = TokenBackend(algorithm='HS256').decode(token, verify=False)
            email = valid_data['email']
        except ValidationError as v:
            print("Validation error", v)
            return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)
        survey = self.model_class.objects.get(id=pk)
        participants = self.serializer_class(survey.participant.all(), many=True).data
        for participant in participants:
            mail_service.send(
                from_email=email,
                to=participant['email'],
                subject=subject,
                template=template,
                context=participant,
                reply_to=None
            )

        return HttpResponse(status=status.HTTP_201_CREATED)


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
class SurveyDuplicateView(viewsets.ViewSet):
    serializer_class = SurveySerializer
    model_class = Survey

    @csrf_exempt
    @transaction.atomic
    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk: int):
        token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
        try:
            valid_data = TokenBackend(algorithm='HS256').decode(token, verify=False)
            user_id = valid_data['user_id']
        except ValidationError as v:
            logging.error("Validation error", v)
            return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)
        exist_survey = self.model_class.objects.get(id=pk)
        new_survey = self.model_class.objects.create(
            title=exist_survey.title + " Copy",
            description=exist_survey.description,
            start_date=exist_survey.start_date,
            end_date=exist_survey.end_date,
            is_active=exist_survey.is_active,
        )

        questions = QuestionSerializer(exist_survey.questions.all(), many=True).data
        for question in questions:
            SurveyQuestion.objects.create(
                survey=new_survey,
                question=Question.objects.get(id=question['id']),
                asked_by=User.objects.get(id=user_id),
            )

        participants = UserSerializer(exist_survey.participant.all(), many=True).data
        for participant in participants:
            ParticipantSurvey.objects.create(
                participant=User.objects.get(id=participant['id']),
                survey=new_survey,
                status="created"
            )

        serializer = self.serializer_class(new_survey)
        return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
class ParticipantSurveyView(viewsets.ModelViewSet):
    lookup_field = 'id'
    queryset = ParticipantSurvey.objects.all()
    serializer_class = PartitionSurveySerializer

    def get_queryset(self):
        return ParticipantSurvey.objects.filter(
            survey_id=self.kwargs['survey_id'])


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
class SurveyQuestionView(viewsets.ModelViewSet):
    lookup_field = 'id'
    queryset = SurveyQuestion.objects.all()
    serializer_class = SurveyQuestionSerializer

    def get_queryset(self):
        return SurveyQuestion.objects.filter(
            survey_id=self.kwargs['survey_id'])


@authentication_classes([JWTAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
class AnswerView(viewsets.ModelViewSet):
    lookup_field = 'id'
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer
