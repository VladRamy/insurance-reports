from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse, JsonResponse
from reports.models import *
from reports.serializers import *
from reports.utils.report_generators import *
import json
from django.db.models import Case, When, FloatField, Sum
from io import BytesIO
import pandas as pd
# import xlsxwriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from rest_framework.generics import ListAPIView
from .models import InsuranceProduct
from .serializers import InsuranceProductSerializer


class ProductListAPI(ListAPIView):
    queryset = InsuranceProduct.objects.all().order_by('id')
    serializer_class = InsuranceProductSerializer
    permission_classes = [IsAuthenticated]

class ReportAPI(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            report_type = request.GET.get('type', 'cashflow')
            params = {
                'start_date': request.GET.get('start_date'),
                'end_date': request.GET.get('end_date'),
                'product_id': request.GET.get('product_id'),
                'region_id': request.GET.get('region_id'),
                'payment_type': request.GET.get('payment_type')
            }
            
            # Валидация дат
            if not params['start_date'] or not params['end_date']:
                return Response(
                    {'error': 'Both start_date and end_date are required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Выбор генератора
            generator_class = self.get_generator_class(report_type)
            if not generator_class:
                return Response(
                    {'error': f'Invalid report type: {report_type}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            generator = generator_class(params)
            data = generator.generate()
            
            return Response({
                'status': 'success',
                'data': data
            })
            
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            print(f"API Error: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def get_generator_class(self, report_type):
        generators = {
            'cashflow': CashFlowReportGenerator,
            'reserves': ReserveReportGenerator,
            'loss_ratio': LossRatioReportGenerator,
            'forecast': PaymentForecastGenerator
        }
        return generators.get(report_type)
    
    def get_report_generator(self, report_type, params):
        """Возвращает соответствующий генератор отчета"""
        generators = {
            'cashflow': CashFlowReportGenerator,
            'reserves': ReserveReportGenerator,
            'loss_ratio': LossRatioReportGenerator,
            'forecast': PaymentForecastGenerator
        }
        
        generator_class = generators.get(report_type)
        if generator_class:
            return generator_class(params)
        return None
    
    def normalize_report_data(self, data, report_type):
        """Приводит данные отчета к единому формату"""
        if not data:
            return []
            
        if report_type == 'cashflow':
            return self._normalize_cashflow_data(data)
        elif report_type == 'reserves':
            return self._normalize_reserves_data(data)
        elif report_type == 'loss_ratio':
            return self._normalize_loss_ratio_data(data)
        elif report_type == 'forecast':
            return self._normalize_forecast_data(data)
        else:
            return data
    
    def _normalize_cashflow_data(self, data):
        """Нормализация данных Cash Flow отчета"""
        normalized = []
        
        for item in data:
            # Проверяем разные возможные варианты имен полей
            date = item.get('date')
            product_name = item.get('product__name') or item.get('product_name')
            expected = float(item.get('expected_sum') or item.get('expected_amount') or 0)
            actual = float(item.get('actual_sum') or item.get('actual_amount') or 0)
            
            normalized.append({
                'date': date,
                'product_name': product_name,
                'expected_amount': expected,
                'actual_amount': actual,
                'difference': actual - expected,
                'accuracy': (actual / expected * 100) if expected else 0
            })
        
        return normalized
    
    def _normalize_reserves_data(self, data):
        """Нормализация данных Reserves отчета"""
        normalized = []
        
        for item in data:
            normalized.append({
                'calculation_date': item.get('calculation_date'),
                'total_reserves': float(item.get('total_reserves') or 0),
                'required_reserves': float(item.get('required_reserves') or 0),
                'available_reserves': float(item.get('available_reserves') or 0),
                'sufficiency_ratio': (
                    (float(item.get('available_reserves') or 0) / 
                    float(item.get('required_reserves') or 1) * 100
                ) if item.get('required_reserves') else 0)
            })
        
        return normalized
    
    def _normalize_loss_ratio_data(self, data):
        """Нормализация данных Loss Ratio отчета"""
        normalized = []
        
        for item in data:
            earned_premium = float(item.get('earned_premium') or 0)
            incurred_losses = float(item.get('incurred_losses') or 0)
            
            normalized.append({
                'product_name': item.get('product__name') or item.get('product_name'),
                'year': item.get('year'),
                'month': item.get('month'),
                'earned_premium': earned_premium,
                'incurred_losses': incurred_losses,
                'loss_ratio': (incurred_losses / earned_premium * 100) if earned_premium else 0
            })
        
        return normalized
    
    def _normalize_forecast_data(self, data):
        """Нормализация данных прогноза"""
        normalized = {
            'historical': [],
            'forecast': []
        }
        
        if isinstance(data, dict):
            # Обработка исторических данных
            for item in data.get('historical', []):
                normalized['historical'].append({
                    'date': item.get('date'),
                    'actual_amount': float(item.get('actual_amount') or 0),
                    'expected_amount': float(item.get('expected_amount') or 0),
                    'forecast_amount': float(item.get('forecast') or 0)
                })
            
            # Обработка прогнозных данных
            for item in data.get('forecast', []):
                normalized['forecast'].append({
                    'date': item.get('date'),
                    'amount': float(item.get('amount') or 0),
                    'type': 'forecast'
                })
        
        return normalized

class ExportReportAPI(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            report_type = request.GET.get('type', '').lower()
            format = request.GET.get('format', 'excel').lower()
            
            if format not in ['excel', 'pdf']:
                raise ValueError("Invalid export format. Supported formats: excel, pdf")
                
            params = {
                'start_date': request.GET.get('start_date'),
                'end_date': request.GET.get('end_date'),
                'product_id': request.GET.get('product_id')
            }
            
            # Валидация параметров
            if not all([params['start_date'], params['end_date']]):
                raise ValueError("Both start_date and end_date are required")
                
            # Генерация данных
            generators = {
                'cashflow': CashFlowReportGenerator,
                'loss_ratio': LossRatioReportGenerator
            }
            
            if report_type not in generators:
                raise ValueError(f"Export not supported for report type: {report_type}")
                
            generator = generators[report_type](params)
            data = generator.generate()
            
            if not data:
                raise ValueError("No data available for the selected parameters")
                
            # Экспорт
            if format == 'excel':
                return self.export_to_excel(data, report_type)
            else:
                return self.export_to_pdf(data, report_type)
                
        except ValueError as e:
            return Response(
                {'status': 'error', 'message': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'status': 'error', 'message': f"Export failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def export_to_excel(self, data, report_type):
        # Создаем DataFrame
        df = pd.DataFrame(data)
        
        # Определяем колонки в зависимости от типа отчета
        if report_type == 'cashflow':
            columns = ['Date', 'Product', 'Expected', 'Actual', 'Difference', 'Accuracy']
            df.columns = columns[:len(df.columns)]
        elif report_type == 'loss_ratio':
            columns = ['Product', 'Year', 'Month', 'Earned Premium', 'Incurred Losses', 'Loss Ratio']
            df.columns = columns[:len(df.columns)]
        
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name=report_type.capitalize(), index=False)
            
            # Форматирование
            workbook = writer.book
            worksheet = writer.sheets[report_type.capitalize()]
            
            header_format = workbook.add_format({
                'bold': True,
                'text_wrap': True,
                'border': 1,
                'bg_color': '#4472C4',
                'font_color': 'white'
            })
            
            for col_num, value in enumerate(columns):
                worksheet.write(0, col_num, value, header_format)
            
            worksheet.autofilter(0, 0, 0, len(columns)-1)
            worksheet.freeze_panes(1, 0)
        
        output.seek(0)
        response = HttpResponse(
            output,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="{report_type}_report.xlsx"'
        return response
    
    def export_to_excel(self, data, title, columns):
        output = BytesIO()
        
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df = pd.DataFrame(data)
            df.to_excel(writer, sheet_name=title[:30], index=False)
            
            workbook = writer.book
            worksheet = writer.sheets[title[:30]]
            
            # Форматирование
            header_format = workbook.add_format({
                'bold': True,
                'text_wrap': True,
                'border': 1,
                'bg_color': '#4472C4',
                'font_color': 'white'
            })
            
            for col_num, value in enumerate(columns):
                worksheet.write(0, col_num, value, header_format)
            
            worksheet.autofilter(0, 0, 0, len(columns)-1)
            worksheet.freeze_panes(1, 0)
            
        output.seek(0)
        response = HttpResponse(
            output.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="{title}.xlsx"'
        return response
    
    def export_to_pdf(self, data, title, columns):
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        
        # Преобразование данных для таблицы
        table_data = [columns]
        for item in data:
            row = []
            for col in columns:
                col_key = col.lower().replace(' ', '_')
                row.append(str(item.get(col_key, '')))
            table_data.append(row)
        
        # Создание таблицы
        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4472C4')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        doc.build([table])
        buffer.seek(0)
        
        response = HttpResponse(buffer.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{title}.pdf"'
        return response

class DashboardAPI(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # Основные метрики для дашборда
        metrics = {
            'total_premium': PaymentFlow.objects.filter(
                payment_type='premium'
            ).aggregate(total=Sum('actual_amount'))['total'] or 0,
            
            'total_claims': PaymentFlow.objects.filter(
                payment_type='claim'
            ).aggregate(total=Sum('actual_amount'))['total'] or 0,
            
            'open_claims': InsuranceClaim.objects.filter(
                status__in=['open', 'processing']
            ).aggregate(total=Sum('reserve'))['total'] or 0,
            
            'policy_count': Policy.objects.count(),
            
            'loss_ratio': self.calculate_loss_ratio(),
            
            'reserve_sufficiency': self.calculate_reserve_sufficiency(),
            
            'top_products': list(
                PaymentFlow.objects.values('product__name').annotate(
                    premium=Sum(
                        Case(
                            When(payment_type='premium', then='actual_amount'),
                            default=0,
                            output_field=FloatField()
                        )
                    ),
                    claims=Sum(
                        Case(
                            When(payment_type='claim', then='actual_amount'),
                            default=0,
                            output_field=FloatField()
                        )
                    )
                ).order_by('-premium')[:5]
            )
        }
        
        return Response(metrics)
    
    def calculate_loss_ratio(self):
        premium = PaymentFlow.objects.filter(
            payment_type='premium'
        ).aggregate(total=Sum('actual_amount'))['total'] or 0
        
        claims = PaymentFlow.objects.filter(
            payment_type='claim'
        ).aggregate(total=Sum('actual_amount'))['total'] or 0
        
        if premium > 0:
            return (claims / premium) * 100
        return 0
    
    def calculate_reserve_sufficiency(self):
        required = InsuranceClaim.objects.filter(
            status__in=['open', 'processing']
        ).aggregate(total=Sum('reserve'))['total'] or 0
        
        available = ReserveCalculation.objects.latest('calculation_date').available_reserves
        
        if required > 0:
            return (available / required) * 100
        return 100