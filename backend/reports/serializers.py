from rest_framework import serializers
from reports.models import *
from django.db.models import Sum, Avg, F, ExpressionWrapper, FloatField
from django.db.models.functions import ExtractMonth, ExtractYear

class InsuranceProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = InsuranceProduct
        fields = '__all__'

class PaymentFlowSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    region_name = serializers.CharField(source='region.name', read_only=True)
    
    class Meta:
        model = PaymentFlow
        fields = '__all__'
        extra_kwargs = {
            'policy': {'required': False},
            'region': {'required': False}
        }

class CashFlowReportSerializer(serializers.Serializer):
    date = serializers.DateField()
    product_name = serializers.CharField()
    expected_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    actual_amount = serializers.DecimalField(max_digits=12, decimal_places=2, allow_null=True)
    difference = serializers.DecimalField(max_digits=12, decimal_places=2, allow_null=True)
    accuracy = serializers.FloatField(allow_null=True)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if data['actual_amount'] is not None:
            data['difference'] = data['actual_amount'] - data['expected_amount']
            if data['expected_amount'] != 0:
                data['accuracy'] = (data['actual_amount'] / data['expected_amount']) * 100
        return data

class ReserveReportSerializer(serializers.ModelSerializer):
    sufficiency_ratio = serializers.SerializerMethodField()
    
    class Meta:
        model = ReserveCalculation
        fields = '__all__'
    
    def get_sufficiency_ratio(self, obj):
        if obj.required_reserves > 0:
            return (obj.available_reserves / obj.required_reserves) * 100
        return 100

class LossRatioReportSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    product_name = serializers.CharField()
    year = serializers.IntegerField()
    month = serializers.IntegerField()
    earned_premium = serializers.DecimalField(max_digits=12, decimal_places=2)
    incurred_losses = serializers.DecimalField(max_digits=12, decimal_places=2)
    loss_ratio = serializers.FloatField()

    def validate(self, data):
        if data['earned_premium'] == 0:
            data['loss_ratio'] = 0.0
        else:
            data['loss_ratio'] = (data['incurred_losses'] / data['earned_premium']) * 100
        return data
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        if data['earned_premium'] > 0:
            data['loss_ratio'] = (data['incurred_losses'] / data['earned_premium']) * 100
        else:
            data['loss_ratio'] = 0.0
        return data