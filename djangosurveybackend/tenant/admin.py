from django.contrib import admin

from tenant.models import Tenant, Service, Unit, Configuration


# Register your models here.
@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ('name', 'subdomain_prefix', 'is_active')
    list_filter = ('name', 'subdomain_prefix', 'is_active')
    fields = ('name', 'subdomain_prefix', 'is_active')


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    list_filter = ('name', 'is_active')
    fields = ('name', 'is_active')


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ('name', 'tenant', 'parent', 'is_active')
    list_filter = ('name', 'tenant', 'is_active')
    fields = ('name', 'tenant', 'parent', 'is_active')


@admin.register(Configuration)
class ConfigurationAdmin(admin.ModelAdmin):
    list_display = ('name', 'value', 'service', 'tenant', 'unit', 'is_active')
    list_filter = ('service', 'tenant', 'unit', 'is_active')
    fields = ('name', 'value', 'service', 'tenant', 'unit', 'is_active')
