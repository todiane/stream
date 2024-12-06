from django.db import migrations
from django.utils import timezone

def create_initial_pages(apps, schema_editor):
    Page = apps.get_model('pages', 'Page')
    Hero = apps.get_model('pages', 'Hero')

    # Create Hero
    Hero.objects.create(
        title="Stream English",
        subtitle="Helping Students Achieve Grade 9",
        content="Welcome to Stream English - Your path to excellence in English Language and Literature.",
        is_active=True
    )

    # Create Homepage
    Page.objects.create(
        title="Homepage",
        slug="home",
        template="home",
        content="""<section class="section bg-white dark:bg-gray-900 py-12">
    <div class="container mx-auto px-4 text-center">
        <h2 class="text-3xl font-extrabold mb-4 text-gray-900 dark:text-white">
            Helping You Thrive
        </h2>
        <p>
            My goal is to help you reach the very highest grades in your English qualifications. 
            I am focused on helping you reach Grade 9.
        </p>
    </div>
</section>""",
        is_active=True,
        publish_date=timezone.now(),
        meta_title="Stream English - Expert English Tutoring",
        meta_description="Expert English tutoring helping students achieve Grade 9 in GCSE English Language and Literature.",
        meta_keywords="English tutor, GCSE English, Grade 9, English Literature, English Language"
    )

    # Create About page
    Page.objects.create(
        title="About",
        slug="about",
        template="about",
        content="""<section class="section bg-white dark:bg-gray-900">
    <div class="py-8 px-4 mx-auto max-w-screen-xl lg:py-16 lg:px-6">
        <!-- Your existing about page content -->
    </div>
</section>""",
        is_active=True,
        publish_date=timezone.now(),
        meta_title="About Stream English - Your Expert English Tutor",
        meta_description="Learn about Stream English and how we help students achieve excellence in English Language and Literature.",
        meta_keywords="English tutor biography, English teaching experience, GCSE English tutor"
    )

def remove_initial_pages(apps, schema_editor):
    Page = apps.get_model('pages', 'Page')
    Hero = apps.get_model('pages', 'Hero')
    Page.objects.all().delete()
    Hero.objects.all().delete()

class Migration(migrations.Migration):
    dependencies = [
        ('pages', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_initial_pages, remove_initial_pages),
    ]
    