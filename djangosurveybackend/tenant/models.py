from django.db import models


# Create your models here.
class Service(models.Model):
    name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)

    @classmethod
    def get_default_pk(cls):
        entity, created = cls.objects.get_or_create(
            name="Master Service",
            defaults=dict(is_active=True),
        )
        return entity.pk

    class Meta:
        verbose_name = "Service"
        verbose_name_plural = "Service"


class Tenant(models.Model):
    name = models.CharField(max_length=100)
    subdomain_prefix = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)

    @classmethod
    def get_default_pk(cls):
        entity, created = cls.objects.get_or_create(
            name="Default Tenant",
            defaults=dict(subdomain_prefix="*", is_active=True),
        )
        return entity.pk

    class Meta:
        verbose_name = "Tenant"
        verbose_name_plural = "Tenants"


class ServiceAwareModel(models.Model):
    service = models.ForeignKey(
        Service, on_delete=models.CASCADE, default=Service.get_default_pk
    )

    class Meta:
        abstract = True


class TenantAwareModel(models.Model):
    tenant = models.ForeignKey(
        Tenant, on_delete=models.CASCADE, default=Tenant.get_default_pk
    )

    class Meta:
        abstract = True


class Unit(TenantAwareModel):
    name = models.CharField(max_length=100)
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    @classmethod
    def get_default_pk(cls):
        entity, created = cls.objects.get_or_create(
            name="Default Unit",
            defaults=dict(is_active=True),
        )
        return entity.pk

    class Meta:
        verbose_name = "Unit"
        verbose_name_plural = "Units"
        unique_together = (("name", "tenant"),)


class UnitAwareModel(TenantAwareModel):
    unit = models.ForeignKey(
        Unit, on_delete=models.CASCADE, default=Unit.get_default_pk
    )

    class Meta:
        abstract = True


class Configuration(UnitAwareModel, ServiceAwareModel):
    name = models.CharField(max_length=100)
    value = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Config"
        verbose_name_plural = "Configs"
        unique_together = (("name", "service", "tenant", "unit"),)
