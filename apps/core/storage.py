from django.conf import settings
from django.core.files.storage import default_storage


def r2_media_storage():
    """Storage for Lesson.video_file/document_file — Cloudflare R2 when configured,
    otherwise falls back to the local default storage (dev machines without R2 set up)."""
    if not settings.USE_R2_STORAGE:
        return default_storage

    from storages.backends.s3 import S3Storage

    return S3Storage()
