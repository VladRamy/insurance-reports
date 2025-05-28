from django.urls import path
from reports.views import *
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('reports/', ReportAPI.as_view(), name='reports-api'),
    path('reports/export/', ExportReportAPI.as_view(), name='export-report'),
    path('dashboard/', DashboardAPI.as_view(), name='dashboard-api'),
    path('auth/', obtain_auth_token, name='api_token_auth'),
    
    # Дополнительные эндпоинты
    # path('api/products/', ProductListAPI.as_view(), name='products-api'),
    # path('api/regions/', RegionListAPI.as_view(), name='regions-api'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)