from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.kpi_pro.views import (
    DashboardRHView,
    DepartmentHeatmapView,
    EmployeeKPIDetailView,
    EmployeeKPIView,
    EmployeeListView,
    MyTrainersToRateView,
    NineBoxView,
    RatableTrainerKPIsView,
    TrainerKPIView,
    TrainerRankingView,
    TrainerRatingViewSet,
)

router = DefaultRouter()
router.register('trainer-ratings', TrainerRatingViewSet, basename='trainer-rating')

urlpatterns = [
    path('employees/', EmployeeKPIView.as_view(), name='kpi-pro-employees'),
    path('employees/list/', EmployeeListView.as_view(), name='kpi-pro-employees-list'),
    path('employees/by-department/', DepartmentHeatmapView.as_view(), name='kpi-pro-employees-by-department'),
    path('employees/<int:user_id>/', EmployeeKPIDetailView.as_view(), name='kpi-pro-employee-detail'),
    path('trainers/', TrainerKPIView.as_view(), name='kpi-pro-trainers'),
    path('trainers/ranking/', TrainerRankingView.as_view(), name='kpi-pro-trainers-ranking'),
    path('trainer-ratings/criteria/', RatableTrainerKPIsView.as_view(), name='kpi-pro-trainer-ratings-criteria'),
    path('trainer-ratings/my-trainers/', MyTrainersToRateView.as_view(), name='kpi-pro-my-trainers'),
    path('dashboard/', DashboardRHView.as_view(), name='kpi-pro-dashboard'),
    path('nine-box/', NineBoxView.as_view(), name='kpi-pro-nine-box'),
] + router.urls
