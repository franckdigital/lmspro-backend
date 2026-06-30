from rest_framework import serializers

from apps.progression.models import ChapterUnlock, ChapterValidation, CourseProgressionSettings, LessonProgress, XAPIStatement


class CourseProgressionSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseProgressionSettings
        fields = '__all__'
        read_only_fields = ('course',)


class LessonProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonProgress
        fields = '__all__'
        read_only_fields = ('user', 'is_completed', 'completed_at')


class LessonProgressUpdateSerializer(serializers.Serializer):
    watched_seconds = serializers.IntegerField(required=False, min_value=0)
    position_seconds = serializers.IntegerField(required=False, min_value=0)
    document_viewed = serializers.BooleanField(required=False)
    time_spent_delta = serializers.IntegerField(required=False, min_value=0, default=0)
    mark_completed = serializers.BooleanField(required=False)


class ChapterValidationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChapterValidation
        fields = '__all__'
        read_only_fields = ('validated_by',)


class ChapterUnlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChapterUnlock
        fields = '__all__'


class ChapterStatusSerializer(serializers.Serializer):
    chapter_id = serializers.IntegerField()
    title = serializers.CharField()
    is_unlocked = serializers.BooleanField()
    is_completed = serializers.BooleanField()


class XAPIStatementSerializer(serializers.ModelSerializer):
    class Meta:
        model = XAPIStatement
        fields = '__all__'
        read_only_fields = ('user', 'timestamp')
