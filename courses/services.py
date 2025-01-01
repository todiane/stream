import logging
from django.core.exceptions import ObjectDoesNotExist
from .models import Course, Lesson

logger = logging.getLogger("django")


def get_publish_courses():
    return Course.objects.filter(status="publish")


def get_course_detail(course_slug=None):
    if not course_slug:
        return None
    try:
        return Course.objects.get(
            slug=course_slug,  # Changed from public_id to slug based on your URL structure
            status="publish",
        )
    except Course.DoesNotExist:
        return None


def get_course_lessons(course_obj=None):
    if not isinstance(course_obj, Course):
        return Lesson.objects.none()

    return course_obj.lesson_set.filter(
        course__status="publish", status__in=["publish", "soon"]
    )


def get_lesson_detail(course_slug=None, lesson_slug=None):
    if not course_slug or not lesson_slug:
        return None

    try:
        return Lesson.objects.select_related("course").get(
            course__slug=course_slug,  # Changed from public_id to slug based on URL
            slug=lesson_slug,  # Changed from public_id to slug based on URL
            course__status="publish",
            status__in=["publish", "soon"],
        )
    except Lesson.DoesNotExist:
        # Log at debug level since this is expected behavior
        logger.debug(f"Lesson not found: {lesson_slug} in course {course_slug}")
        return None
    except Exception as e:
        # Log unexpected errors at error level
        logger.error(f"Error getting lesson detail: {str(e)}")
        return None
