from celery import shared_task
from reports.utils.report_generators import *
from django.core.mail import EmailMessage
from django.conf import settings
import time
from io import BytesIO

@shared_task
def generate_async_report(report_type, params, email):
    try:
        if report_type == 'cashflow':
            generator = CashFlowReportGenerator(params)
        elif report_type == 'reserves':
            generator = ReserveReportGenerator(params)
        # ... другие отчеты
        
        data = generator.generate()
        
        # Генерация файла
        if params.get('format') == 'excel':
            output = BytesIO()
            df = pd.DataFrame(data)
            df.to_excel(output, index=False)
            output.seek(0)
            
            # Отправка по email
            email = EmailMessage(
                f"Your {report_type} report",
                "Please find attached the requested report.",
                settings.DEFAULT_FROM_EMAIL,
                [email]
            )
            email.attach(
                f"{report_type}_report.xlsx",
                output.getvalue(),
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            email.send()
            
        return {'status': 'success', 'email': email}
        
    except Exception as e:
        return {'status': 'error', 'message': str(e)}