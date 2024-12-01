from django.db import migrations
from django.utils.text import slugify

def generate_slugs_and_public_ids(apps, schema_editor):
    Course = apps.get_model('courses', 'Course')
    for course in Course.objects.all():
        if not course.slug:
            course.slug = slugify(course.title)
        if not course.public_id:
            from courses.models import generate_public_id
            course.public_id = generate_public_id(course)
        course.save()

class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(generate_slugs_and_public_ids),
    ]
    