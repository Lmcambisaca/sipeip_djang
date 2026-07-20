from django.urls import path
from . import views

urlpatterns = [

    path("generar/", views.generar_reporte, name="generar_reporte"),

    path("consultar/", views.consultar_reportes, name="consultar_reportes"),

    path("pdf/<str:tipo>/", views.reporte_pdf, name="reporte_pdf"),

    path("excel/<str:tipo>/", views.reporte_excel, name="reporte_excel"),
    
    path("reporte_consolidado/", views.reporte_consolidado, name="reporte_consolidado"),

]