from django.db import models


class SurveyParticipantStatus:
    PENDING = "pending"
    IN_PROGRESS = "in progress"
    DONE = "done"


class LogicalOperator(models.TextChoices):
    LOGICAL_OPERATOR_AND = "AND"
    LOGICAL_OPERATOR_NOT = "NOT"
    LOGICAL_OPERATOR_OR = "OR"


class MathematicalOperator(models.TextChoices):
    MATH_OPERATOR_EQUAL = "EQ"
    MATH_OPERATOR_LESS_THAN_OR_EQUAL = "LTE"
    MATH_OPERATOR_GREATER_THAN_OR_EQUAL = "GTE"
    MATH_OPERATOR_LESS_THAN = "LT"
    MATH_OPERATOR_GREATER_THAN = "GT"
    MATH_OPERATOR_IN = "IN"
    MATH_OPERATOR_NOT_IN = "NIN"
