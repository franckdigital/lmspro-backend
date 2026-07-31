from django.urls import path

from apps.kpi_pro.views import (
    DashboardRHView,
    DepartmentHeatmapView,
    EmployeeKPIDetailView,
    EmployeeKPIView,
    NineBoxView,
    TrainerKPIView,
    TrainerRankingView,
)

urlpatterns = [
    path('employees/', EmployeeKPIView.as_view(), name='kpi-pro-employees'),
    path('employees/by-department/', DepartmentHeatmapView.as_view(), name='kpi-pro-employees-by-department'),
    path('employees/<int:user_id>/', EmployeeKPIDetailView.as_view(), name='kpi-pro-employee-detail'),
    path('trainers/', TrainerKPIView.as_view(), name='kpi-pro-trainers'),
    path('trainers/ranking/', TrainerRankingView.as_view(), name='kpi-pro-trainers-ranking'),
    path('dashboard/', DashboardRHView.as_view(), name='kpi-pro-dashboard'),
    path('nine-box/', NineBoxView.as_view(), name='kpi-pro-nine-box'),
]
