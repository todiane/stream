# courses/services.py
from .models import Course, Lesson


def get_publish_courses():
    return Course.objects.filter(status="publish")


def get_course_detail(course_slug=None):
    if course_slug is None:
        return None
    obj = None
    try:
        obj = Course.objects.get(status="publish", public_id=course_slug)
    except:
        pass
    return obj


def get_course_lessons(course_obj=None):
    lessons = Lesson.objects.none()
    if not isinstance(course_obj, Course):
        return lessons
    lessons = course_obj.lesson_set.filter(
        course__status="publish", status__in=["publish", "soon"]
    )
    return lessons


def get_lesson_detail(course_slug=None, lesson_slug=None):
    if lesson_slug is None and course_slug is None:
        return None
    obj = None
    try:
        obj = Lesson.objects.get(
            course__public_id=course_slug,
            course__status="publish",
            status__in=["publish", "soon"],
            public_id=lesson_slug,
        )
    except Exception as e:
        print("lesson detail", e)
        pass
    return obj
