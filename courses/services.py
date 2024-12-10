# courses/services.py

from .models import Course, Lesson, PublishStatus


def get_publish_courses():
    return Course.objects.filter(status=PublishStatus.PUBLISHED)

def get_course_detail(course_slug=None):
    if course_slug is None:
        return None
    obj = None
    try:
        obj = Course.objects.get(
            status=PublishStatus.PUBLISHED,
            public_id=course_slug
        )
    except:
        pass
    return obj

def get_course_lessons(course_obj=None):
    lessons = Lesson.objects.none()
    if not isinstance(course_obj, Course):
        return lessons
    lessons = course_obj.lesson_set.filter(
        course__status=PublishStatus.PUBLISHED,
        status__in=[PublishStatus.PUBLISHED, PublishStatus.COMING_SOON]
    )
    return lessons


def get_lesson_detail(course_slug=None, lesson_slug=None):
    if lesson_slug is None and course_slug is None:
        return None
    obj = None
    try:
        obj = Lesson.objects.get(
            course__public_id=course_slug,
            course__status=PublishStatus.PUBLISHED,
            status__in=[PublishStatus.PUBLISHED, PublishStatus.COMING_SOON],
            public_id=lesson_slug
        )
    except Exception as e:
        print("lesson detail", e)
        pass
    return obj