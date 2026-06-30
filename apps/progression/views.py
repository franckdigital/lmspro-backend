from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.constants import Roles
from apps.core.permissions import HasRole
from apps.progression.models import ChapterValidation, CourseProgressionSettings, LessonProgress, XAPIStatement
from apps.progression.serializers import (
    ChapterStatusSerializer,
    ChapterValidationSerializer,
    CourseProgressionSettingsSerializer,
    LessonProgressSerializer,
    LessonProgressUpdateSerializer,
    XAPIStatementSerializer,
)
from apps.progression.services import is_chapter_completed, is_chapter_unlocked, is_final_exam_unlocked, is_lesson_accessible, ordered_chapters, record_lesson_progress

IsContentManager = HasRole.for_roles(Roles.TRAINER, Roles.COMPANY_ADMIN)
IsValidator = HasRole.for_roles(Roles.TRAINER, Roles.MANAGER, Roles.HR, Roles.COMPANY_ADMIN)


class CourseProgressionSettingsViewSet(viewsets.ModelViewSet):
    queryset = CourseProgressionSettings.objects.select_related('course').all()
    serializer_class = CourseProgressionSettingsSerializer
    permission_classes = [IsContentManager]
    filterset_fields = ['course']


class CourseProgressView(APIView):
    """Returns the lock/unlock status of every chapter in a course for the current learner —
    the data needed to render the §24.1 sequential progression UI."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, course_id):
        from apps.courses.models import Course

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

        return Response({
            'chapters': ChapterStatusSerializer(rows, many=True).data,
            'final_exam_unlocked': is_final_exam_unlocked(request.user, course),
        })


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
