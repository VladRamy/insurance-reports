from django.contrib import admin
from .models import *

@admin.register(InsuranceProduct)
class InsuranceProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'base_premium', 'risk_factor')
    search_fields = ('name',)

@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'economic_factor')
    list_filter = ('economic_factor',)

@admin.register(Policy)
class PolicyAdmin(admin.ModelAdmin):
    list_display = ('policy_number', 'product', 'status', 'premium')
    list_filter = ('status', 'product')
    search_fields = ('policy_number',)

@admin.register(PaymentFlow)
class PaymentFlowAdmin(admin.ModelAdmin):
    list_display = ('date', 'payment_type', 'expected_amount', 'actual_amount')
    list_filter = ('payment_type', 'product')
    date_hierarchy = 'date'

@admin.register(InsuranceClaim)
class InsuranceClaimAdmin(admin.ModelAdmin):
    list_display = ('claim_number', 'policy', 'status', 'estimated_amount')
    list_filter = ('status', 'is_catastrophic')
    search_fields = ('claim_number',)

@admin.register(ReserveCalculation)
class ReserveCalculationAdmin(admin.ModelAdmin):
    list_display = ('calculation_date', 'product', 'total_reserves')
    list_filter = ('product',)
    date_hierarchy = 'calculation_date'
    
