import base64
import json
import logging

from dependency_injector.wiring import inject, Provide
from django.contrib.auth.models import User, Group
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.db import transaction
from django.http import HttpResponse, JsonResponse, Http404
from django.utils.decorators import method_decorator
from django.utils.module_loading import import_string
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.vary import vary_on_headers
from drfpasswordless.services import TokenService
from drfpasswordless.settings import api_settings
from drfpasswordless.views import ObtainEmailCallbackToken
from rest_framework import viewsets, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes, permission_classes, action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.backends import TokenBackend

from authenticate.models import ExpiredToken
from authenticate.views import ObtainAuthTokenFromCallbackRedirectToken
from surveybackend import Container, settings
from surveybackend.services import MailService
from surveys.models import Question, QuestionOption, Survey, Answer, SurveyQuestion, ParticipantSurvey, QuestionType
from surveys.scheduler import send_callback_token, scheduler, cancel_survey_reminder
from surveys.serializers import QuestionSerializer, QuestionOptionSerializer, SurveySerializer, AnswerSerializer, \
    SurveyQuestionSerializer, PartitionSurveySerializer, QuestionTypeSerializer, UserSerializer, GroupSerializer, \
    TenantEmailAuthSerializer

CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)


class CachedModelViewView(viewsets.ModelViewSet):

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


# Create your views here.
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
class UserView(CachedModelViewView):
    lookup_field = 'id'
    queryset = import_string(settings.AUTH_USER_MODEL_MODULE).objects.all()
    serializer_class = UserSerializer


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
class GroupView(CachedModelViewView):
    lookup_field = 'id'
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
class QuestionTypeView(CachedModelViewView):
    lookup_field = 'id'
    queryset = QuestionType.objects.all()
    serializer_class = QuestionTypeSerializer


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
class QuestionView(CachedModelViewView):
    lookup_field = 'id'
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
class QuestionOptionView(CachedModelViewView):
    lookup_field = 'id'
    queryset = QuestionOption.objects.all()
    serializer_class = QuestionOptionSerializer

    def get_queryset(self):
        return QuestionOption.objects.filter(question_id=self.kwargs['question_id'])


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
class SurveyView(CachedModelViewView):
    lookup_field = 'id'
    queryset = Survey.objects.all()
    serializer_class = SurveySerializer


@authentication_classes([JWTAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
class SubmitSurveyView(CachedModelViewView):
    lookup_field = 'id'
    queryset = Survey.objects.all()
    serializer_class = SurveySerializer

    @csrf_exempt
    @transaction.atomic
    @action(detail=True, methods=['post'], url_name='submit')
    def submit(self, request, id: int):
        token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
        try:
            user = ExpiredToken.objects.get(key=token).user
        except ValidationError as v:
            print("Validation error", v)
            return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)
        survey = Survey.objects.get(id=id)
        data = json.loads(request.body.decode('utf-8')).get('data')
        for item in data:
            question = survey.questions.get(id=item.get('question'))
            answer = item.get('answer')
            content = answer.get('content')
            if content is not None and isinstance(content, str) and len(content) > 0:
                Answer.objects.create(
                    question=question,
                    survey=survey,
                    content=content,
                    answered_by=user
                )

            options = answer.get('options')
            if options is not None and isinstance(options, list):
                for option in options:
                    Answer.objects.create(
                        question=question,
                        survey=survey,
                        option=question.options.get(id=option),
                        answered_by=user
                    )

        serializer = self.serializer_class(survey)

        def _cancel_survey_reminder():
            cancel_survey_reminder(email=user.email, survey_id=str(id))

        transaction.on_commit(_cancel_survey_reminder)
        return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)


@authentication_classes([JWTAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
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
class SurveyAnswerStatisticView(viewsets.ViewSet):
    serializer_class = SurveySerializer
    model_class = Survey

    @csrf_exempt
    @action(detail=True, methods=['get'])
    def statistics(self, request, pk: int):
        try:
            exist_survey = self.model_class.objects.get(id=pk)
        except self.model_class.DoesNotExist:
            raise Http404()

        questions = QuestionSerializer(exist_survey.questions.all(), many=True).data

        def get_statistics_by_question(_question):
            def translate_each_statistic(answer):
                value = answer.option_content if answer.option_content is not None else answer.text_content
                result = {"value": value, "count": answer.frequency}
                if hasattr(answer, 'username'):
                    result['user'] = getattr(answer, 'username')
                    del result['count']
                return result

            question_id = _question['id']
            question_content = _question['content']
            question_type = _question['question_type']
            question_type_entity = QuestionTypeSerializer(QuestionType.objects.get(id=question_type), many=False).data
            question_type_name = question_type_entity['name']
            function = 'get_survey_answer_statistics_by_user' \
                if question_type_name == "Comment" else 'get_survey_answer_statistics'
            answers = Answer.objects.raw(f"SELECT 1 as ID, * FROM public.{function}({pk},{question_id})")
            statistics = list(map(translate_each_statistic, answers))
            logging.info(f"Get statistics with survey {pk} - question {question_id}")
            return {
                "question": question_content,
                "question_type": question_type_name,
                "statistics": statistics
            }

        data = list(map(get_statistics_by_question, questions))
        return JsonResponse({"data": data}, status=status.HTTP_200_OK)


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
class ParticipantSurveyView(CachedModelViewView):
    lookup_field = 'id'
    queryset = ParticipantSurvey.objects.all()
    serializer_class = PartitionSurveySerializer

    def get_queryset(self):
        return ParticipantSurvey.objects.filter(
            survey_id=self.kwargs['survey_id'])


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
class SurveyQuestionView(CachedModelViewView):
    lookup_field = 'id'
    queryset = SurveyQuestion.objects.all()
    serializer_class = SurveyQuestionSerializer

    def get_queryset(self):
        return SurveyQuestion.objects.filter(
            survey_id=self.kwargs['survey_id'])


@authentication_classes([JWTAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
class AnswerView(CachedModelViewView):
    lookup_field = 'id'
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer


@authentication_classes([])
@permission_classes([AllowAny])
class ObtainTenantEmailCallbackToken(ObtainEmailCallbackToken):
    serializer_class = TenantEmailAuthSerializer

    @transaction.atomic
    @inject
    def post(self, request, mail_service: MailService = Provide[Container.mail_service], *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            user = serializer.validated_data['user']
            survey = serializer.validated_data['survey']
            link = serializer.validated_data['redirect_link_patterns']
            job_id = f"{user}_survey_{survey}"
            survey_entity = Survey.objects.get(id=survey)

            def _send_callback_token():
                scheduler.add_job(
                    send_callback_token,
                    id=job_id,
                    kwargs={
                        "token_service_class": TokenService,
                        "mail_service": mail_service,
                        "user": user,
                        "survey": survey,
                        "redirect_link_patterns": link,
                        "alias_type": self.alias_type,
                        "token_type": self.token_type,
                        "survey_end_time": survey_entity.end_date
                    },
                    replace_existing=True,
                )

            transaction.on_commit(_send_callback_token)
            return Response({"message": self.success_response}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.error_messages, status=status.HTTP_400_BAD_REQUEST)


@authentication_classes([])
@permission_classes([AllowAny])
class ObtainSurveyAuthTokenFromCallbackRedirectToken(ObtainAuthTokenFromCallbackRedirectToken):

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        request_data = json.loads(base64.b64decode(request.data.get('token')))
        serializer = self.serializer_class(data=request_data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.validated_data["user"]
            token_creator = import_string(api_settings.PASSWORDLESS_AUTH_TOKEN_CREATOR)
            (token, _) = token_creator(user)

            if token:
                TokenSerializer = import_string(api_settings.PASSWORDLESS_AUTH_TOKEN_SERIALIZER)
                token_serializer = TokenSerializer(data=token.__dict__, partial=True, context={"request": request})
                survey = Survey.objects.get(id=request_data['survey'])
                survey_serializer = SurveySerializer(survey)
                if not ParticipantSurvey.objects.filter(participant=user.id, survey=request_data['survey']).exists():
                    ParticipantSurvey.objects.create(
                        participant=user,
                        survey=survey,
                        status='joined',
                    )
                if token_serializer.is_valid():
                    # Return our key for consumption.
                    return Response({
                        **token_serializer.data,
                        "survey": survey_serializer.data
                    }, status=status.HTTP_200_OK)
        else:
            logging.error("Couldn't log in unknown user. Errors on serializer: {}".format(serializer.error_messages))
        return Response({"detail": "Couldn't log you in. Try again later."}, status=status.HTTP_400_BAD_REQUEST)
