from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import Group
from django.db import transaction
from django.utils.module_loading import import_string
from drfpasswordless.serializers import EmailAuthSerializer
from drfpasswordless.settings import api_settings
from rest_framework import serializers
from rest_framework_simplejwt.backends import TokenBackend

from core.serializer.validators import remove_non_updatable
from surveys.models import Survey, Question, QuestionOption, ParticipantSurvey, SurveyQuestion, Answer, QuestionType
from tenant.models import Tenant, Service, Unit, Configuration


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = import_string(settings.AUTH_USER_MODEL_MODULE)
        fields = '__all__'


class NestedParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = import_string(settings.AUTH_USER_MODEL_MODULE)
        fields = ['id', 'username', 'email', 'is_active']


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'


class QuestionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionType
        fields = '__all__'


class QuestionOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionOption
        fields = '__all__'


class NestedQuestionOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionOption
        fields = ['id', 'content', 'is_active']


class NestedQuestionSerializer(serializers.ModelSerializer):
    options = NestedQuestionOptionSerializer(many=True)
    question_type = QuestionTypeSerializer(many=False, read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'content', 'question_type', 'options', 'is_active']


class SimpleNestedQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'content']


class QuestionSerializer(serializers.ModelSerializer):
    options = NestedQuestionOptionSerializer(many=True)

    class Meta:
        model = Question
        fields = '__all__'
        non_updatable_fields = ['options', 'question_created_by', 'question_created_at']

    @transaction.atomic
    def create(self, validated_data):
        options = validated_data.pop('options')
        question = super().create(validated_data)
        for option in options:
            option['question'] = question
        self.fields['options'].create(options)
        return question

    @transaction.atomic
    @remove_non_updatable(non_updatable_fields=Meta.non_updatable_fields)
    def update(self, instance, validated_data):
        return super().update(instance, validated_data)


class PartitionSurveySerializer(serializers.ModelSerializer):
    class Meta:
        model = ParticipantSurvey
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['participant'] = NestedParticipantSerializer(instance.participant, many=False).data
        return data


class SurveyQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurveyQuestion
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["survey"] = SurveySerializer(instance.survey, many=False).data
        data['question'] = NestedQuestionSerializer(instance.question, many=False).data
        data['asked_by'] = NestedParticipantSerializer(instance.asked_by, many=False).data
        return data


class CustomSurveyQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurveyQuestion
        fields = ['question', 'is_active']


class NestedSurveySerializer(serializers.ModelSerializer):
    class Meta:
        model = Survey
        fields = ['id', 'title', 'start_date', 'end_date', 'is_active']


class SurveySerializer(serializers.ModelSerializer):
    questions = NestedQuestionSerializer(many=True, read_only=True)
    participant = NestedParticipantSerializer(many=True, read_only=True)
    survey_questions = CustomSurveyQuestionSerializer(many=True, required=False)

    class Meta:
        model = Survey
        fields = '__all__'
        non_updatable_fields = ['questions', 'survey_questions', 'participant']

    @transaction.atomic
    def create(self, validated_data):
        request = self.context.get('request', None)
        token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
        valid_data = TokenBackend(algorithm='HS256').decode(token, verify=False)
        user_id = valid_data['user_id']
        survey_questions = validated_data.pop('survey_questions')
        survey = super().create(validated_data)
        user = import_string(settings.AUTH_USER_MODEL_MODULE).objects.get(id=user_id)
        for survey_question in survey_questions:
            survey_question['survey'] = survey
            survey_question['asked_by'] = user
        SurveyQuestionSerializer(many=True).create(survey_questions)
        return survey

    @transaction.atomic
    @remove_non_updatable(non_updatable_fields=Meta.non_updatable_fields)
    def update(self, instance, validated_data):
        updated_survey = super().update(instance, validated_data)
        return updated_survey


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["survey"] = NestedSurveySerializer(instance.survey, many=False).data
        data['option'] = NestedQuestionOptionSerializer(instance.option, many=False).data
        data['question'] = SimpleNestedQuestionSerializer(instance.question, many=False).data
        data['answered_by'] = NestedParticipantSerializer(instance.answered_by, many=False).data
        return data


class NestedAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['id', 'option', 'content']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['option'] = NestedQuestionSerializer(instance.option, many=False).data
        data['question'] = NestedQuestionSerializer(instance.question, many=False).data
        return data


User = get_user_model()


class TenantEmailAuthSerializer(EmailAuthSerializer):
    tenant = serializers.IntegerField()
    unit = serializers.IntegerField()
    service = serializers.IntegerField()
    survey = serializers.IntegerField()

    def validate(self, attrs):
        tenant = attrs.get('tenant')
        if not tenant or not Tenant.objects.filter(id=tenant):
            raise serializers.ValidationError("Tenant is not found")

        service = attrs.get('service')
        if not service or not Service.objects.filter(id=service):
            raise serializers.ValidationError("Service is not found")

        unit = attrs.get('unit')
        if not unit or not Unit.objects.filter(id=unit):
            raise serializers.ValidationError("Unit is not found")

        survey = attrs.get('survey')
        if not survey or not Survey.objects.filter(id=survey):
            raise serializers.ValidationError("Survey is not found")

        if not Configuration.objects.select_related().filter(
                tenant=tenant, service=service, unit=unit, name='Redirect Link Patterns').exists():
            raise serializers.ValidationError("Redirect Link Patterns is not found")

        config = Configuration.objects.select_related().filter(
            tenant=tenant, service=service, unit=unit, name='Redirect Link Patterns').first()
        redirect_link_patterns = config.value
        attrs['redirect_link_patterns'] = redirect_link_patterns

        alias = attrs.get(self.alias_type)

        if alias:
            # Create or authenticate a user
            # Return THem

            if api_settings.PASSWORDLESS_REGISTER_NEW_USERS is True:
                # If new aliases should register new users.
                try:
                    user = User.objects.get(**{self.alias_type + '__iexact': alias})
                except User.DoesNotExist:
                    user = User.objects.create(**{self.alias_type: alias}, username=alias)
                    user.set_unusable_password()
                    user.save()
            else:
                # If new aliases should not register new users.
                try:
                    user = User.objects.get(**{self.alias_type + '__iexact': alias})
                except User.DoesNotExist:
                    user = None

            if user:
                if not user.is_active:
                    # If valid, return attrs so we can create a token in our logic controller
                    msg = _('User account is disabled.')
                    raise serializers.ValidationError(msg)
            else:
                msg = _('No account is associated with this alias.')
                raise serializers.ValidationError(msg)
        else:
            msg = _('Missing %s.') % self.alias_type
            raise serializers.ValidationError(msg)

        attrs['user'] = user
        return attrs
