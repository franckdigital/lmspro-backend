from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.progression.views import (
    ChapterValidationViewSet,
    CourseProgressionSettingsViewSet,
    CourseProgressView,
    LessonAccessView,
    LessonProgressViewSet,
    XAPIStatementViewSet,
)

router = DefaultRouter()
router.register('progression-settings', CourseProgressionSettingsViewSet, basename='progression-settings')
router.register('lesson-progress', LessonProgressViewSet, basename='lesson-progress')
router.register('chapter-validations', ChapterValidationViewSet, basename='chapter-validation')
router.register('xapi-statements', XAPIStatementViewSet, basename='xapi-statement')

urlpatterns = [
    path('courses/<int:course_id>/progress/', CourseProgressView.as_view(), name='course-progress'),
    path('lessons/<int:lesson_id>/access/', LessonAccessView.as_view(), name='lesson-access'),
] + router.urls
