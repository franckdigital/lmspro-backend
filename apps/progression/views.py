from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.constants import Roles
from apps.core.permissions import HasRole
from apps.progression.models import ChapterUnlock, ChapterValidation, CourseProgressionSettings, LessonProgress, XAPIStatement
from apps.progression.serializers import (
    ChapterStatusSerializer,
    ChapterValidationSerializer,
    CourseProgressionSettingsSerializer,
    LessonProgressSerializer,
    LessonProgressUpdateSerializer,
    XAPIStatementSerializer,
)
from apps.progression.services import (
    get_progression_settings,
    is_chapter_completed,
    is_chapter_unlocked,
    is_final_exam_unlocked,
    is_lesson_accessible,
    ordered_chapters,
    record_lesson_progress,
)

IsContentManager = HasRole.for_roles(Roles.TRAINER, Roles.COMPANY_ADMIN)
IsValidator = HasRole.for_roles(Roles.TRAINER, Roles.MANAGER, Roles.HR, Roles.COMPANY_ADMIN)


class CourseProgressionSettingsViewSet(viewsets.ModelViewSet):
    queryset = CourseProgressionSettings.objects.select_related('course').all()
    serializer_class = CourseProgressionSettingsSerializer
    permission_classes = [IsContentManager]
    filterset_fields = ['course']


class CourseProgressView(APIView):
    """Returns the lock/unlock status of every chapter in a course for the current learner —
    the data needed to render the §24.1 sequential progression UI, plus the course-level final
    exam's availability (learner must be at 100% lesson progress) and attempt history."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, course_id):
        from apps.assessments.models import Assessment, AssessmentAttempt
        from apps.courses.models import Course, Enrollment

        course = Course.objects.get(pk=course_id)
        chapters = ordered_chapters(course)

        rows = []
        for chapter in chapters:
            rows.append({
                'chapter_id': chapter.id,
                'title': chapter.title,
                'is_unlocked': is_chapter_unlocked(request.user, chapter),
                'is_completed': is_chapter_completed(request.user, chapter),
            })

        enrollment = Enrollment.objects.filter(user=request.user, course=course).first()
        progress_percent = float(enrollment.progress_percent) if enrollment else 0

        final_exam_data = None
        final_exam = Assessment.objects.filter(course=course, chapter__isnull=True, is_published=True).first()
        if final_exam:
            settings = get_progression_settings(course)
            effective_max = final_exam.max_attempts
            if settings.max_attempts is not None:
                effective_max = min(effective_max, settings.max_attempts)

            attempts = list(
                AssessmentAttempt.objects.filter(assessment=final_exam, user=request.user).order_by('-attempt_number')
            )
            scores = [float(a.score) for a in attempts if a.score is not None]
            final_exam_data = {
                'id': final_exam.id,
                'title': final_exam.title,
                'passing_score': 100,
                'max_attempts': effective_max,
                'attempts_used': len(attempts),
                'attempts_remaining': max(0, effective_max - len(attempts)),
                'best_score': max(scores) if scores else None,
                'has_passed': any(score >= 100 for score in scores),
                'is_unlocked': progress_percent >= 100,
            }

        return Response({
            'chapters': ChapterStatusSerializer(rows, many=True).data,
            'final_exam_unlocked': is_final_exam_unlocked(request.user, course),
            'progress_percent': progress_percent,
            'final_exam': final_exam_data,
        })


class CourseProgressResetView(APIView):
    """Resets the current learner's progress for a course (all lesson completions, chapter
    unlocks/validations, and the enrollment's progress_percent/status) so they can retake it
    from scratch. Used by the "return to course" choice on the completion modal."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, course_id):
        from apps.courses.models import Course, Enrollment

        course = Course.objects.get(pk=course_id)
        try:
            enrollment = Enrollment.objects.get(user=request.user, course=course)
        except Enrollment.DoesNotExist:
            return Response({'detail': "Vous n'êtes pas inscrit à cette formation."}, status=404)

        LessonProgress.objects.filter(user=request.user, lesson__chapter__section__course=course).delete()
        ChapterUnlock.objects.filter(user=request.user, chapter__section__course=course).delete()
        ChapterValidation.objects.filter(user=request.user, chapter__section__course=course).delete()

        enrollment.progress_percent = 0
        enrollment.status = Enrollment.STATUS_IN_PROGRESS
        enrollment.completed_at = None
        enrollment.save(update_fields=['progress_percent', 'status', 'completed_at'])

        return Response({'detail': 'Progression réinitialisée.'})


class LessonAccessView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, lesson_id):
        from apps.courses.models import Lesson

        lesson = Lesson.objects.select_related('chapter').get(pk=lesson_id)
        accessible = is_lesson_accessible(request.user, lesson)
        return Response({'lesson_id': lesson.id, 'is_accessible': accessible})


class LessonProgressViewSet(viewsets.ModelViewSet):
    serializer_class = LessonProgressSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['lesson']
    http_method_names = ['get', 'post', 'head', 'options']

    def get_queryset(self):
        return LessonProgress.objects.filter(user=self.request.user).select_related('lesson')

    @action(detail=False, methods=['post'], url_path='update')
    def update_progress(self, request):
        from apps.courses.models import Lesson

        lesson_id = request.data.get('lesson_id')
        lesson = Lesson.objects.select_related('chapter').get(pk=lesson_id)

        if not is_lesson_accessible(request.user, lesson):
            return Response({'detail': 'Ce chapitre est verrouillé.'}, status=403)

        serializer = LessonProgressUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = dict(serializer.validated_data)
        scorm_completed = data.pop('mark_completed', None)
        progress = record_lesson_progress(request.user, lesson, scorm_completed=scorm_completed, **data)
        return Response(LessonProgressSerializer(progress).data)


class ChapterValidationViewSet(viewsets.ModelViewSet):
    queryset = ChapterValidation.objects.select_related('chapter', 'user', 'validated_by').all()
    serializer_class = ChapterValidationSerializer
    permission_classes = [IsValidator]
    filterset_fields = ['chapter', 'user']

    def perform_create(self, serializer):
        serializer.save(validated_by=self.request.user)


class XAPIStatementViewSet(viewsets.ModelViewSet):
    serializer_class = XAPIStatementSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post', 'head', 'options']
    filterset_fields = ['verb', 'object_type']

    def get_queryset(self):
        user = self.request.user
        qs = XAPIStatement.objects.all()
        if user.is_superuser or user.role in (Roles.SUPER_ADMIN, Roles.HR, Roles.COMPANY_ADMIN):
            return qs
        return qs.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, raw_statement=self.request.data)
