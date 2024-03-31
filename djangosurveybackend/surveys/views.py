import base64
import json
import logging

from dependency_injector.wiring import Provide, inject
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.db import transaction
from django.http import Http404, HttpResponse, JsonResponse
from django.utils import timezone
from django.utils.module_loading import import_string
from django.views.decorators.csrf import csrf_exempt
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from drfpasswordless.services import TokenService
from drfpasswordless.settings import api_settings
from drfpasswordless.views import ObtainEmailCallbackToken
from rest_framework import status, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action, authentication_classes, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.backends import TokenBackend

from authenticate.models import ExpiredToken
from authenticate.views import ObtainAuthTokenFromCallbackRedirectToken
from surveybackend import Container, settings
from surveybackend.services import MailService
from surveys.constants import SurveyParticipantStatus, LogicalOperator
from surveys.models import (
    Answer,
    ParticipantSurvey,
    Question,
    QuestionOption,
    QuestionType,
    Survey,
    SurveyQuestion,
    SurveySubmit,
    SurveyQuestionSet,
    SurveyQuestionCondition,
)
from surveys.scheduler import cancel_survey_reminder, scheduler, send_callback_token
from surveys.serializers import (
    AnswerSerializer,
    GroupSerializer,
    PartitionSurveySerializer,
    QuestionOptionSerializer,
    QuestionSerializer,
    QuestionTypeSerializer,
    SurveyQuestionSerializer,
    SurveySerializer,
    TenantEmailAuthSerializer,
    UserSerializer,
    SurveySubmitSerializer,
    SurveyQuestionSetSerializer,
    SurveyQuestionConditionSerializer,
    CreateSurveyQuestionSerializer,
    CreateSurveyQuestionConditionSerializer,
)

CACHE_TTL = getattr(settings, "CACHE_TTL", DEFAULT_TIMEOUT)


# Create your views here.
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
class UserView(viewsets.ModelViewSet):
    lookup_field = "id"
    queryset = import_string(settings.AUTH_USER_MODEL_MODULE).objects.all()
    serializer_class = UserSerializer


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
class GroupView(viewsets.ModelViewSet):
    lookup_field = "id"
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
class QuestionTypeView(viewsets.ModelViewSet):
    lookup_field = "id"
    queryset = QuestionType.objects.all()
    serializer_class = QuestionTypeSerializer


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
class QuestionView(viewsets.ModelViewSet):
    lookup_field = "id"
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.is_editable:
            return super().update(request, *args, **kwargs)
        return JsonResponse(
            status=status.HTTP_400_BAD_REQUEST,
            data={"message": "Question is not editable"},
        )

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.is_editable:
            return super().partial_update(request, *args, **kwargs)
        return JsonResponse(
            status=status.HTTP_400_BAD_REQUEST,
            data={"message": "Question is not editable"},
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.is_deletable:
            return super().destroy(request, *args, **kwargs)
        return JsonResponse(
            status=status.HTTP_400_BAD_REQUEST,
            data={"message": "Question is not deletable"},
        )


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
class QuestionOptionView(viewsets.ModelViewSet):
    lookup_field = "id"
    queryset = QuestionOption.objects.all()
    serializer_class = QuestionOptionSerializer

    def get_queryset(self):
        return QuestionOption.objects.filter(question_id=self.kwargs["question_id"])


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
class SurveyView(viewsets.ModelViewSet):
    lookup_field = "id"
    queryset = Survey.objects.all()
    serializer_class = SurveySerializer


@authentication_classes([JWTAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
class SubmitSurveyView(viewsets.ModelViewSet):
    lookup_field = "id"
    queryset = Survey.objects.all()
    serializer_class = SurveySerializer

    @csrf_exempt
    @transaction.atomic
    @action(detail=True, methods=["post"], url_name="submit")
    def submit(self, request, id: int):
        token = request.META.get("HTTP_AUTHORIZATION", " ").split(" ")[1]
        try:
            user = ExpiredToken.objects.get(key=token).user
        except ValidationError as v:
            print("Validation error", v)
            return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)
        survey = Survey.objects.get(id=id)
        data = json.loads(request.body.decode("utf-8")).get("data")
        for item in data:
            question = survey.questions.get(id=item.get("question"))
            answer = item.get("answer")
            content = answer.get("content")
            if content is not None and isinstance(content, str) and len(content) > 0:
                Answer.objects.create(
                    question=question, survey=survey, content=content, answered_by=user
                )

            options = answer.get("options")
            if options is not None and isinstance(options, list):
                for option in options:
                    Answer.objects.create(
                        question=question,
                        survey=survey,
                        option=question.options.get(id=option),
                        answered_by=user,
                    )

        def _handle_post_submit_survey():
            try:
                ParticipantSurvey.objects.update_or_create(
                    participant=user.id,
                    survey=id,
                    defaults={
                        "participant": user,
                        "survey": survey,
                        "status": SurveyParticipantStatus.DONE,
                    },
                )
                logging.info("Update participant status to done")
            except Exception as e:
                logging.error(e, stack_info=True)
            SurveySubmit.objects.create(
                survey_id=id, submitted_by=user, submitted_at=timezone.now()
            )
            cancel_survey_reminder(email=user.email, survey_id=str(id))

        transaction.on_commit(_handle_post_submit_survey)
        return JsonResponse(
            {"message": "Submit successfully"}, status=status.HTTP_201_CREATED
        )


@authentication_classes([JWTAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
class NextSetSurveyView(viewsets.ViewSet):
    model = SurveyQuestionSet
    serializer_class = SurveyQuestionSetSerializer

    @csrf_exempt
    @action(detail=False, methods=["post"], url_name="next")
    def next(self, request, *args, **kwargs):
        data = json.loads(request.body.decode("utf-8")).get("data")
        items = data.get("items")
        exclude_sets = [str(i) for i in data.get("exclude_sets")]
        if (
            str(kwargs["set_id"]) not in exclude_sets
            or kwargs["set_id"] not in exclude_sets
        ):
            exclude_sets.append(str(kwargs["set_id"]))
        answers = []
        for item in items:
            survey_question = SurveyQuestion.objects.filter(
                set_id=kwargs["set_id"],
                survey_id=kwargs["survey_id"],
                question_id=item.get("question"),
            )

            if not survey_question.exists() or survey_question.first() is None:
                continue

            answer = item.get("answer")
            value = None
            if "content" in answer.keys():
                value = answer.get("content")
            elif "options" in answer.keys():
                options = answer.get("options")
                if (
                    options is not None
                    and isinstance(options, list)
                    and len(options) > 0
                ):
                    value = QuestionOption.objects.get(id=options[0]).content
            answers.append(
                {"survey_question": survey_question.first().id, "value": value}
            )

        question_sets = list(
            filter(
                lambda s: str(s.id) not in exclude_sets,
                list(
                    SurveyQuestionSet.objects.filter(
                        survey_id=kwargs["survey_id"]
                    ).all()
                ),
            )
        )
        for question_set in question_sets:
            is_passes = True
            for condition in list(
                SurveyQuestionCondition.objects.filter(set_id=question_set.id)
            ):
                value = None
                for answer in answers:
                    if answer["survey_question"] == condition.survey_question.id:
                        value = answer["value"]
                        break

                if value is not None:
                    if (
                        condition.logical_operator
                        == LogicalOperator.LOGICAL_OPERATOR_AND
                    ):
                        is_passes = is_passes and condition.check_condition(value)
                    elif (
                        condition.logical_operator
                        == LogicalOperator.LOGICAL_OPERATOR_OR
                    ):
                        is_passes = is_passes or condition.check_condition(value)
                else:
                    is_passes = False
                    break

            if is_passes:
                serializer = self.serializer_class(question_set)
                return JsonResponse(serializer.data, status=status.HTTP_200_OK)

        return HttpResponse(status=status.HTTP_404_NOT_FOUND)


@authentication_classes([JWTAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
class NotifyParticipantView(viewsets.ViewSet):
    serializer_class = UserSerializer
    model_class = Survey

    @csrf_exempt
    @transaction.atomic
    @action(detail=True, methods=["post"], url_name="notify")
    @inject
    def notify(
        self,
        request,
        pk: int,
        mail_service: MailService = Provide[Container.mail_service],
        subject: str = Provide[Container.config.SURVEY_SUBJECT],
        template: str = Provide[Container.config.SURVEY_TEMPLATE],
    ):
        token = request.META.get("HTTP_AUTHORIZATION", " ").split(" ")[1]
        try:
            valid_data = TokenBackend(algorithm="HS256").decode(token, verify=False)
            email = valid_data["email"]
        except ValidationError as v:
            print("Validation error", v)
            return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)
        survey = self.model_class.objects.get(id=pk)
        participants = self.serializer_class(survey.participant.all(), many=True).data
        for participant in participants:
            mail_service.send(
                from_email=email,
                to=participant["email"],
                subject=subject,
                template=template,
                context=participant,
                reply_to=None,
            )

        return HttpResponse(status=status.HTTP_201_CREATED)


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
class SurveyDuplicateView(viewsets.ViewSet):
    serializer_class = SurveySerializer
    model_class = Survey

    @csrf_exempt
    @transaction.atomic
    @action(detail=True, methods=["post"])
    def duplicate(self, request, pk: int):
        token = request.META.get("HTTP_AUTHORIZATION", " ").split(" ")[1]
        try:
            valid_data = TokenBackend(algorithm="HS256").decode(token, verify=False)
            user_id = valid_data["user_id"]
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
                question=Question.objects.get(id=question["id"]),
                asked_by=import_string(settings.AUTH_USER_MODEL_MODULE).objects.get(
                    id=user_id
                ),
            )

        participants = UserSerializer(exist_survey.participant.all(), many=True).data
        for participant in participants:
            ParticipantSurvey.objects.create(
                participant=import_string(settings.AUTH_USER_MODEL_MODULE).objects.get(
                    id=participant["id"]
                ),
                survey=new_survey,
                status=participant["status"],
            )

        serializer = self.serializer_class(new_survey)
        return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
class SurveyAnswerStatisticView(viewsets.ViewSet):
    serializer_class = SurveySerializer
    model_class = Survey

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "page", OpenApiTypes.INT, OpenApiParameter.QUERY, default=1
            ),
            OpenApiParameter(
                "page_size", OpenApiTypes.INT, OpenApiParameter.QUERY, default=1
            ),
        ]
    )
    @csrf_exempt
    @action(detail=True, methods=["get"])
    def statistics(self, request, pk: int):
        try:
            exist_survey = self.model_class.objects.get(id=pk)
        except self.model_class.DoesNotExist:
            raise Http404()

        questions: list = QuestionSerializer(
            exist_survey.questions.all(), many=True
        ).data
        total = len(questions)
        try:
            page = int(request.query_params["page"])
            page_size = int(request.query_params["page_size"])
            questions = [
                questions[i : i + page_size]
                for i in range(0, len(questions), page_size)
            ][page - 1]
        except Exception:
            questions = []

        def get_statistics_by_question(_question):
            def translate_each_statistic(answer):
                value = (
                    answer.option_content
                    if answer.option_content is not None
                    else answer.text_content
                )
                result = {"value": value, "count": answer.frequency}
                if hasattr(answer, "username"):
                    result["user"] = getattr(answer, "username")
                    del result["count"]
                return result

            question_id = _question["id"]
            question_content = _question["content"]
            question_type = _question["question_type"]
            question_type_entity = QuestionTypeSerializer(
                QuestionType.objects.get(id=question_type), many=False
            ).data
            question_type_name = question_type_entity["name"]
            function = (
                "get_survey_answer_statistics_by_user"
                if question_type_name == "Comment"
                else "get_survey_answer_statistics"
            )
            answers = Answer.objects.raw(
                f"SELECT 1 as ID, * FROM public.{function}({pk},{question_id})"
            )
            statistics = list(map(translate_each_statistic, answers))
            logging.info(f"Get statistics with survey {pk} - question {question_id}")
            return {
                "question": question_content,
                "question_type": question_type_name,
                "statistics": statistics,
            }

        data = list(map(get_statistics_by_question, questions))
        return JsonResponse({"data": data, "total": total}, status=status.HTTP_200_OK)


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
class ParticipantSurveyView(viewsets.ModelViewSet):
    lookup_field = "id"
    queryset = ParticipantSurvey.objects.all()
    serializer_class = PartitionSurveySerializer

    def get_queryset(self):
        return ParticipantSurvey.objects.filter(survey_id=self.kwargs["survey_id"])


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
class ActivateParticipantSurveyView(viewsets.ViewSet):
    model_class = ParticipantSurvey
    serializer_class = PartitionSurveySerializer

    @extend_schema(request=None)
    @csrf_exempt
    @transaction.atomic
    @action(detail=True, methods=["patch"])
    def activate(self, request, pk: int):
        token = request.META.get("HTTP_AUTHORIZATION", " ").split(" ")[1]
        try:
            TokenBackend(algorithm="HS256").decode(token, verify=False)
        except ValidationError as v:
            logging.error("Validation error", v)
            return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)
        try:
            exist_participant = self.model_class.objects.get(id=pk)
        except self.model_class.DoesNotExist as e:
            logging.error(e)
            return HttpResponse(status=status.HTTP_404_NOT_FOUND)
        exist_participant.is_active = True
        exist_participant.save()
        return HttpResponse(status=status.HTTP_200_OK)


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
class DeactivateParticipantSurveyView(viewsets.ViewSet):
    model_class = ParticipantSurvey
    serializer_class = PartitionSurveySerializer

    @extend_schema(request=None)
    @csrf_exempt
    @transaction.atomic
    @action(detail=True, methods=["patch"])
    def deactivate(self, request, pk: int):
        token = request.META.get("HTTP_AUTHORIZATION", " ").split(" ")[1]
        try:
            TokenBackend(algorithm="HS256").decode(token, verify=False)
        except ValidationError as v:
            logging.error("Validation error", v)
            return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)
        try:
            exist_participant = self.model_class.objects.get(id=pk)
        except self.model_class.DoesNotExist as e:
            logging.error(e)
            return HttpResponse(status=status.HTTP_404_NOT_FOUND)
        exist_participant.is_active = False
        exist_participant.save()
        return HttpResponse(status=status.HTTP_200_OK)


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
class SurveyQuestionSetView(viewsets.ModelViewSet):
    lookup_field = "id"
    queryset = SurveyQuestionSet.objects.all()
    serializer_class = SurveyQuestionSetSerializer

    def get_queryset(self):
        return SurveyQuestionSet.objects.filter(survey_id=self.kwargs["survey_id"])

    @extend_schema(request=None)
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        token = request.META.get("HTTP_AUTHORIZATION", " ").split(" ")[1]
        try:
            valid_data = TokenBackend(algorithm="HS256").decode(token, verify=False)
            user_id = valid_data["user_id"]
        except ValidationError as v:
            logging.error("Validation error", v)
            return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)

        try:
            Survey.objects.get(id=kwargs["survey_id"])
        except Survey.DoesNotExist as e:
            return JsonResponse({"message": str(e)}, status=status.HTTP_404_NOT_FOUND)

        request.data["survey"] = kwargs["survey_id"]
        request.data["set_created_by"] = user_id
        return super().create(request, *args, **kwargs)


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
class SurveyQuestionConditionView(viewsets.ModelViewSet):
    lookup_field = "id"
    queryset = SurveyQuestionCondition.objects.all()
    serializer_class = SurveyQuestionConditionSerializer

    def get_queryset(self):
        return SurveyQuestionCondition.objects.filter(set_id=self.kwargs["set_id"])

    @extend_schema(request=CreateSurveyQuestionConditionSerializer)
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        token = request.META.get("HTTP_AUTHORIZATION", " ").split(" ")[1]
        try:
            valid_data = TokenBackend(algorithm="HS256").decode(token, verify=False)
            user_id = valid_data["user_id"]
        except ValidationError as v:
            logging.error("Validation error", v)
            return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)
        request.data["condition_created_by"] = user_id
        request.data["set"] = kwargs["set_id"]
        return super().create(request, *args, **kwargs)


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
class SurveyQuestionView(viewsets.ModelViewSet):
    lookup_field = "id"
    queryset = SurveyQuestion.objects.all()
    serializer_class = SurveyQuestionSerializer

    def get_queryset(self):
        return SurveyQuestion.objects.filter(
            survey_id=self.kwargs["survey_id"], set_id=self.kwargs["set_id"]
        )

    @extend_schema(request=CreateSurveyQuestionSerializer)
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        token = request.META.get("HTTP_AUTHORIZATION", " ").split(" ")[1]
        try:
            valid_data = TokenBackend(algorithm="HS256").decode(token, verify=False)
            user_id = valid_data["user_id"]
        except ValidationError as v:
            logging.error("Validation error", v)
            return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)
        question_id = request.data["question"]
        survey_id = kwargs["survey_id"]
        set_id = kwargs["set_id"]
        count = SurveyQuestion.objects.filter(survey=survey_id).count()
        request.data["order"] = count
        request.data["asked_by"] = user_id
        request.data["set"] = set_id
        request.data["survey"] = survey_id
        result = super().create(request, *args, **kwargs)
        question = Question.objects.select_for_update().get(id=question_id)
        if question is not None and (question.is_editable or question.is_deletable):
            question.is_editable = False
            question.is_deletable = False
            question.save()
        return result

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        survey = instance.survey
        if survey is None or survey.start_date < timezone.now():
            raise ValidationError(
                "Survey is already start. Cannot remove question out of survey"
            )

        result = super().destroy(request, *args, **kwargs)
        question = instance.question
        if (
            question is not None
            and SurveyQuestion.objects.filter(question=question.id).count() == 0
        ):
            question.is_editable = True
            question.is_deletable = True
            question.save()
        return result


@authentication_classes([JWTAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
class AnswerView(viewsets.ModelViewSet):
    lookup_field = "id"
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer


@authentication_classes([])
@permission_classes([AllowAny])
class ObtainTenantEmailCallbackToken(ObtainEmailCallbackToken):
    serializer_class = TenantEmailAuthSerializer

    @transaction.atomic
    @inject
    def post(
        self,
        request,
        mail_service: MailService = Provide[Container.mail_service],
        *args,
        **kwargs,
    ):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid(raise_exception=True):
            user = serializer.validated_data["user"]
            survey = serializer.validated_data["survey"]
            link = serializer.validated_data["redirect_link_patterns"]
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
                        "survey_end_time": survey_entity.end_date,
                    },
                    replace_existing=True,
                )

            transaction.on_commit(_send_callback_token)
            return Response(
                {"message": self.success_response}, status=status.HTTP_200_OK
            )
        else:
            return Response(
                serializer.error_messages, status=status.HTTP_400_BAD_REQUEST
            )


@authentication_classes([])
@permission_classes([AllowAny])
class ObtainSurveyAuthTokenFromCallbackRedirectToken(
    ObtainAuthTokenFromCallbackRedirectToken
):
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        request_data = json.loads(base64.b64decode(request.data.get("token")))
        serializer = self.serializer_class(data=request_data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.validated_data["user"]
            token_creator = import_string(api_settings.PASSWORDLESS_AUTH_TOKEN_CREATOR)
            (token, _) = token_creator(user)

            if token:
                TokenSerializer = import_string(
                    api_settings.PASSWORDLESS_AUTH_TOKEN_SERIALIZER
                )
                token_serializer = TokenSerializer(
                    data=token.__dict__, partial=True, context={"request": request}
                )
                survey = Survey.objects.get(id=request_data["survey"])
                survey_serializer = SurveySerializer(survey)
                participant = ParticipantSurvey.objects.filter(
                    participant=user.id, survey=request_data["survey"]
                )
                if not participant.exists():
                    ParticipantSurvey.objects.create(
                        participant=user,
                        survey=survey,
                        status=SurveyParticipantStatus.IN_PROGRESS,
                    )
                    logging.info("Update participant status to in progress")
                elif not participant.first().is_active:
                    return Response(
                        {"detail": "Participant is deactivated"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                if token_serializer.is_valid():
                    # Return our key for consumption.
                    return Response(
                        {**token_serializer.data, "survey": survey_serializer.data},
                        status=status.HTTP_200_OK,
                    )
        else:
            logging.error(
                "Couldn't log in unknown user. Errors on serializer: {}".format(
                    serializer.error_messages
                )
            )
        return Response(
            {"detail": "Couldn't log you in. Try again later."},
            status=status.HTTP_400_BAD_REQUEST,
        )


@authentication_classes([JWTAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
class SurveySubmitView(viewsets.ReadOnlyModelViewSet):
    lookup_field = "id"
    queryset = SurveySubmit.objects.all()
    serializer_class = SurveySubmitSerializer
