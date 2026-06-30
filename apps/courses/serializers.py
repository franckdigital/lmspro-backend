from rest_framework import serializers

from apps.courses.models import (
    Chapter,
    Course,
    CourseSection,
    Enrollment,
    Lesson,
    LessonAnswer,
    LessonQuestion,
    LessonResource,
    Review,
    ScormRegistration,
    TrainingRequest,
)


class LessonResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonResource
        fields = '__all__'


class ScormRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScormRegistration
        fields = '__all__'
        read_only_fields = ('user', 'lesson', 'last_accessed_at')


class ScormCommitSerializer(serializers.Serializer):
    cmi = serializers.DictField()


class LessonSerializer(serializers.ModelSerializer):
    resources = LessonResourceSerializer(many=True, read_only=True)

    class Meta:
        model = Lesson
        fields = '__all__'


class LessonLightSerializer(serializers.ModelSerializer):
    """Used for nested listing without exposing raw file URLs (DRM: streaming goes through content_security)."""

    class Meta:
        model = Lesson
        fields = ('id', 'title', 'order', 'content_type', 'duration_seconds', 'is_preview_free')


class LessonResourceLightSerializer(serializers.ModelSerializer):
    """Resource metadata for learners — the raw `file` URL is never exposed; access goes
    through content_security's resource ticket/streaming endpoints (§25)."""

    class Meta:
        model = LessonResource
        fields = ('id', 'title', 'download_allowed')


class LessonPlayerSerializer(serializers.ModelSerializer):
    """Learner-facing lesson detail — deliberately excludes video_file/document_file/
    scorm_package (raw URLs would bypass the secure-streaming/DRM layer in content_security)."""

    resources = LessonResourceLightSerializer(many=True, read_only=True)
    has_media = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = (
            'id', 'chapter', 'title', 'order', 'content_type', 'text_content', 'transcript',
            'duration_seconds', 'is_preview_free', 'external_embed_url', 'resources', 'has_media',
        )

    def get_has_media(self, obj):
        return bool(obj.video_file or obj.document_file or obj.scorm_package)


class ChapterSerializer(serializers.ModelSerializer):
    lessons = LessonLightSerializer(many=True, read_only=True)

    class Meta:
        model = Chapter
        fields = '__all__'


class CourseSectionSerializer(serializers.ModelSerializer):
    chapters = ChapterSerializer(many=True, read_only=True)

    class Meta:
        model = CourseSection
        fields = '__all__'


class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)

    class Meta:
        model = Review
        fields = '__all__'
        read_only_fields = ('user',)


class CourseListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    instructor_name = serializers.CharField(source='instructor.get_full_name', read_only=True)

    class Meta:
        model = Course
        fields = (
            'id', 'title', 'slug', 'subtitle', 'thumbnail', 'category', 'category_name', 'instructor',
            'instructor_name', 'level', 'status', 'price', 'is_free', 'is_company_internal', 'average_rating',
            'total_students', 'total_duration_minutes', 'company',
        )


class CourseDetailSerializer(serializers.ModelSerializer):
    sections = CourseSectionSerializer(many=True, read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)
    instructor_name = serializers.CharField(source='instructor.get_full_name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Course
        fields = '__all__'
        read_only_fields = ('slug', 'average_rating', 'total_students')


class EnrollmentSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)
    course_thumbnail = serializers.ImageField(source='course.thumbnail', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)

    class Meta:
        model = Enrollment
        fields = '__all__'
        read_only_fields = ('user', 'progress_percent', 'status', 'completed_at', 'enrolled_at')


class LessonAnswerSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)

    class Meta:
        model = LessonAnswer
        fields = '__all__'
        read_only_fields = ('author', 'is_instructor_answer')


class LessonQuestionSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    answers = LessonAnswerSerializer(many=True, read_only=True)

    class Meta:
        model = LessonQuestion
        fields = '__all__'
        read_only_fields = ('author',)


class AssignCourseSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    course_id = serializers.IntegerField()
    due_date = serializers.DateField(required=False, allow_null=True)


class TrainingRequestSerializer(serializers.ModelSerializer):
    requested_by_name = serializers.SerializerMethodField(read_only=True)
    for_user_name = serializers.SerializerMethodField(read_only=True)
    course_title = serializers.SerializerMethodField(read_only=True)
    reviewed_by_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = TrainingRequest
        fields = '__all__'
        read_only_fields = ('requested_by', 'reviewed_by', 'reviewed_at', 'status')

    def get_requested_by_name(self, obj):
        return obj.requested_by.get_full_name() or obj.requested_by.email

    def get_for_user_name(self, obj):
        if obj.for_user:
            return obj.for_user.get_full_name() or obj.for_user.email
        return None

    def get_course_title(self, obj):
        return obj.course.title if obj.course_id else None

    def get_reviewed_by_name(self, obj):
        if obj.reviewed_by:
            return obj.reviewed_by.get_full_name() or obj.reviewed_by.email
        return None
