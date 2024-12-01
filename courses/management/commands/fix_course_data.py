from django.core.management.base import BaseCommand
from courses.models import Course
from django.utils.text import slugify

class Command(BaseCommand):
    help = 'Fix missing slugs and public_ids in courses'

    def handle(self, *args, **options):
        courses = Course.objects.all()
        fixed_count = 0
        
        for course in courses:
            modified = False
            
            if not course.slug:
                course.slug = slugify(course.title)
                modified = True
                
            if not course.public_id:
                from courses.models import generate_public_id
                course.public_id = generate_public_id(course)
                modified = True
                
            if modified:
                course.save()
                fixed_count += 1
                self.stdout.write(self.style.SUCCESS(
                    f'Fixed course: {course.title} (slug: {course.slug}, public_id: {course.public_id})'
                ))
        
        self.stdout.write(self.style.SUCCESS(f'Fixed {fixed_count} courses'))
        