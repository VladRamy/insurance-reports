import pandas as pd
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from django.db.models import Q, Sum, Avg, F, ExpressionWrapper, FloatField
from django.db.models.functions import ExtractMonth, ExtractYear
from reports.models import *
import numpy as np
from reports.serializers import *
from django.db.models import Case, When, FloatField
# from scipy import stats

class BaseReportGenerator:
    def __init__(self, params):
        self.params = params
        self.start_date = params.get('start_date')
        self.end_date = params.get('end_date')
        self.product_id = params.get('product_id')
        self.region_id = params.get('region_id')
        self.payment_type = params.get('payment_type')
        self.base_queryset = self.get_base_queryset()

    def get_base_queryset(self):
        queryset = PaymentFlow.objects.filter(
            date__gte=self.start_date,
            date__lte=self.end_date
        )
        
        if self.product_id:
            queryset = queryset.filter(product_id=self.product_id)
            
        if self.region_id:
            queryset = queryset.filter(region_id=self.region_id)
            
        if self.payment_type:
            queryset = queryset.filter(payment_type=self.payment_type)
            
        return queryset.select_related('product', 'region')

    def generate(self):
        raise NotImplementedError

class CashFlowReportGenerator(BaseReportGenerator):
    def generate(self):
        queryset = self.base_queryset.values(
            'date',
            'product__name'
        ).annotate(
            expected_amount=Sum('expected_amount'),
            actual_amount=Sum('actual_amount')
        ).order_by('date')
        
        # Вручную преобразуем данные, так как это не ModelSerializer
        result = []
        for item in queryset:
            result.append({
                'date': item['date'],
                'product_name': item['product__name'],
                'expected_amount': item['expected_amount'],
                'actual_amount': item['actual_amount'],
                'difference': (item['actual_amount'] - item['expected_amount']) if item['actual_amount'] else None,
                'accuracy': (item['actual_amount'] / item['expected_amount'] * 100) if item['expected_amount'] else None
            })
        return result

class ReserveReportGenerator(BaseReportGenerator):
    def generate(self):
        # Расчет резервов по методу Chain Ladder
        claims = InsuranceClaim.objects.filter(
            event_date__lte=self.end_date,
            status__in=['open', 'processing', 'paid']
        )
        
        if self.product_id:
            claims = claims.filter(policy__product_id=self.product_id)
            
        development_data = claims.annotate(
            development_year=ExtractYear('event_date'),
            development_month=ExtractMonth('event_date')
        ).values(
            'development_year',
            'development_month'
        ).annotate(
            total_reserve=Sum('reserve'),
            total_paid=Sum('paid_amount')
        ).order_by('development_year', 'development_month')
        
        # Расчет достаточности резервов
        reserve_calculations = ReserveCalculation.objects.filter(
            calculation_date__range=(self.start_date, self.end_date)
        )
        
        if self.product_id:
            reserve_calculations = reserve_calculations.filter(product_id=self.product_id)
            
        return ReserveReportSerializer(reserve_calculations, many=True).data

class LossRatioReportGenerator(BaseReportGenerator):
    def generate(self):
        try:
            # Получаем данные по премиям и убыткам
            monthly_data = self.base_queryset.annotate(
                year=ExtractYear('date'),
                month=ExtractMonth('date')
            ).values(
                'product_id',
                'product__name',
                'year',
                'month'
            ).annotate(
                earned_premium=Sum(
                    Case(
                        When(payment_type='premium', then='actual_amount'),
                        default=0,
                        output_field=FloatField()
                    )
                ),
                incurred_losses=Sum(
                    Case(
                        When(payment_type='claim', then='actual_amount'),
                        default=0,
                        output_field=FloatField()
                    )
                )
            ).order_by('product_id', 'year', 'month')

            # Добавляем расчет убыточности
            result = []
            for item in monthly_data:
                earned = item['earned_premium'] or 0
                losses = item['incurred_losses'] or 0
                loss_ratio = (losses / earned * 100) if earned > 0 else 0
                
                result.append({
                    'product_id': item['product_id'],
                    'product_name': item['product__name'],
                    'year': item['year'],
                    'month': item['month'],
                    'earned_premium': float(earned),
                    'incurred_losses': float(losses),
                    'loss_ratio': float(loss_ratio)
                })
            
            return result

        except Exception as e:
            print(f"Error generating loss ratio report: {str(e)}")
            raise ValueError("Failed to generate loss ratio report")

class PaymentForecastGenerator(BaseReportGenerator):
    def generate(self):
        try:
            # Получаем исторические данные
            history = self.get_historical_data()
            
            if not history:
                return {
                    'historical': [],
                    'forecast': [],
                    'message': 'No historical data available'
                }
            
            # Группируем по месяцам
            df = pd.DataFrame(list(history.values(
                'date', 'actual_amount', 'expected_amount'
            )))
            
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
            monthly = df.resample('M').sum()
            
            # Простой прогноз (скользящее среднее)
            forecast_values = monthly['actual_amount'].rolling(3).mean().iloc[-1]
            
            # Формируем прогноз на 6 месяцев вперед
            last_date = monthly.index[-1]
            forecast_dates = pd.date_range(
                start=last_date + pd.offsets.MonthBegin(1),
                periods=6,
                freq='M'
            )
            
            return {
                'historical': monthly.reset_index().to_dict('records'),
                'forecast': [{
                    'date': date.strftime('%Y-%m-%d'),
                    'amount': float(forecast_values)
                } for date in forecast_dates]
            }
            
        except Exception as e:
            print(f"Forecast error: {str(e)}")
            return {
                'error': str(e),
                'historical': [],
                'forecast': []
            }

    def validate_params(self):
        """Проверка обязательных параметров"""
        if not hasattr(self, 'start_date') or not self.start_date:
            raise ValueError("Start date is required")
        if not hasattr(self, 'end_date') or not self.end_date:
            raise ValueError("End date is required")
        if not hasattr(self, 'payment_type') or not self.payment_type:
            raise ValueError("Payment type is required")

    def get_historical_data(self):
        """Получение исторических данных с проверкой"""
        try:
            history_start = datetime.strptime(self.start_date, '%Y-%m-%d') - relativedelta(years=2)
            end_date = datetime.strptime(self.end_date, '%Y-%m-%d')
            
            queryset = PaymentFlow.objects.filter(
                date__gte=history_start,
                date__lte=end_date,
                payment_type=self.payment_type
            )
            
            if self.product_id:
                queryset = queryset.filter(product_id=self.product_id)
            if self.region_id:
                queryset = queryset.filter(region_id=self.region_id)
                
            return queryset
            
        except ValueError as e:
            raise ValueError(f"Invalid date format: {str(e)}")

    def calculate_forecast(self, queryset):
        """Основная логика прогнозирования с обработкой ошибок"""
        try:
            # Конвертация в DataFrame
            df = pd.DataFrame(list(queryset.values(
                'date', 'expected_amount', 'actual_amount'
            )))
            
            if df.empty:
                return {
                    'historical': [],
                    'forecast': [],
                    'message': 'No data available after filtering'
                }
            
            # Работа с датами
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
            
            # Определение частоты группировки
            date_range = (datetime.strptime(self.end_date, '%Y-%m-%d') - 
                         datetime.strptime(self.start_date, '%Y-%m-%d')).days
            freq = 'M' if date_range > 90 else 'W'
            
            # Группировка и расчет скользящего среднего
            grouped = df.resample(freq).agg({
                'actual_amount': 'sum',
                'expected_amount': 'sum'
            }).dropna()
            
            if grouped.empty:
                return {
                    'historical': [],
                    'forecast': [],
                    'message': 'Not enough data for forecasting'
                }
            
            window_size = min(3, len(grouped))  # Адаптивный размер окна
            grouped['forecast'] = grouped['actual_amount'].rolling(window=window_size).mean()
            
            # Прогнозирование
            last_date = grouped.index[-1]
            forecast_dates = pd.date_range(
                start=last_date + pd.Timedelta(days=1),
                periods=6,
                freq=freq
            )
            
            forecast_value = grouped['forecast'].iloc[-1] if not grouped['forecast'].isna().all() else 0
            forecast_values = [forecast_value] * len(forecast_dates)
            
            return {
                'historical': grouped.reset_index().to_dict('records'),
                'forecast': [
                    {'date': d.strftime('%Y-%m-%d'), 'amount': float(a)} 
                    for d, a in zip(forecast_dates, forecast_values)
                ]
            }
            
        except Exception as e:
            raise ValueError(f"Forecast calculation failed: {str(e)}")

class StressTestingGenerator:
    def __init__(self, product_id=None, scenario='medium'):
        self.product_id = product_id
        self.scenario = scenario
        self.scenarios = {
            'low': 1.2,
            'medium': 1.5,
            'high': 2.0,
            'extreme': 3.0
        }
    
    def generate(self):
        # Базовые данные о премиях и убытках
        claims = InsuranceClaim.objects.all()
        payments = PaymentFlow.objects.filter(payment_type='claim')
        
        if self.product_id:
            claims = claims.filter(policy__product_id=self.product_id)
            payments = payments.filter(product_id=self.product_id)
            
        # Основные метрики
        total_premium = PaymentFlow.objects.filter(
            payment_type='premium'
        ).aggregate(total=Sum('actual_amount'))['total'] or 0
        
        total_claims = claims.aggregate(
            total_paid=Sum('paid_amount'),
            total_reserve=Sum('reserve')
        )
        
        # Применяем стресс-фактор
        stress_factor = self.scenarios.get(self.scenario, 1.5)
        stressed_claims = total_claims['total_paid'] * stress_factor
        
        return {
            'scenario': self.scenario,
            'stress_factor': stress_factor,
            'total_premium': total_premium,
            'normal_claims': total_claims['total_paid'],
            'stressed_claims': stressed_claims,
            'reserves': total_claims['total_reserve'],
            'impact': (stressed_claims - total_claims['total_paid']) / total_premium * 100
        }