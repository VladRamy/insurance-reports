from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse, JsonResponse
from reports.models import *
from reports.serializers import *
from reports.utils.report_generators import *
import json
from django.db.models import Case, When, FloatField
from io import BytesIO
import pandas as pd
# import xlsxwriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors

class ReportAPI(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        report_type = request.GET.get('type')
        if not report_type:
            return Response(
                {'error': 'Report type not specified'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        params = {
            'start_date': request.GET.get('start_date'),
            'end_date': request.GET.get('end_date'),
            'product_id': request.GET.get('product_id'),
            'region_id': request.GET.get('region_id'),
            'payment_type': request.GET.get('payment_type')
        }
        
        try:
            if report_type == 'cashflow':
                generator = CashFlowReportGenerator(params)
            elif report_type == 'reserves':
                generator = ReserveReportGenerator(params)
            elif report_type == 'loss_ratio':
                generator = LossRatioReportGenerator(params)
            elif report_type == 'forecast':
                generator = PaymentForecastGenerator(params)
            elif report_type == 'stress_test':
                generator = StressTestingGenerator(
                    product_id=params.get('product_id'),
                    scenario=request.GET.get('scenario', 'medium')
                )
            else:
                return Response(
                    {'error': 'Invalid report type'},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            data = generator.generate()
            return Response(data)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ExportReportAPI(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        report_type = request.GET.get('type')
        format = request.GET.get('format', 'excel')
        
        if format not in ['excel', 'pdf']:
            return Response(
                {'error': 'Invalid export format'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        params = {
            'start_date': request.GET.get('start_date'),
            'end_date': request.GET.get('end_date'),
            'product_id': request.GET.get('product_id')
        }
        
        try:
            if report_type == 'cashflow':
                generator = CashFlowReportGenerator(params)
                data = generator.generate()
                title = "Cash Flow Report"
                columns = ['Date', 'Product', 'Expected', 'Actual', 'Difference']
                
            elif report_type == 'loss_ratio':
                generator = LossRatioReportGenerator(params)
                data = generator.generate()
                title = "Loss Ratio Report"
                columns = ['Product', 'Year', 'Month', 'Earned Premium', 'Incurred Losses', 'Loss Ratio']
                
            else:
                return Response(
                    {'error': 'Export not available for this report type'},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            if format == 'excel':
                return self.export_to_excel(data, title, columns)
            else:
                return self.export_to_pdf(data, title, columns)
                
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
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