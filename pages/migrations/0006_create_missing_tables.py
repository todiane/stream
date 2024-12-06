from django.db import migrations

def forwards_func(apps, schema_editor):
    try:
        # Try to create tables if they don't exist
        schema_editor.execute("""
            CREATE TABLE IF NOT EXISTS "pages_aboutme" (
                "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                "title" varchar(200) NOT NULL DEFAULT 'About Me',
                "subtitle" varchar(200) NOT NULL,
                "description" text NOT NULL,
                "qualifications" text NOT NULL,
                "image" varchar(255) NULL,
                "is_active" boolean NOT NULL DEFAULT 1
            )
        """)

        schema_editor.execute("""
            CREATE TABLE IF NOT EXISTS "pages_abouttuition" (
                "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                "title" varchar(200) NOT NULL DEFAULT 'Tuition Lessons',
                "description" text NOT NULL,
                "booking_title" varchar(200) NOT NULL DEFAULT 'Book Your Session',
                "booking_description" text NOT NULL,
                "booking_button_text" varchar(50) NOT NULL DEFAULT 'Book HERE!',
                "booking_button_url" varchar(200) NOT NULL DEFAULT '/booking-form/',
                "is_active" boolean NOT NULL DEFAULT 1
            )
        """)

        schema_editor.execute("""
            CREATE TABLE IF NOT EXISTS "pages_aboutcourses" (
                "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                "title" varchar(200) NOT NULL DEFAULT 'Take A Look At My Latest Courses',
                "description" text NOT NULL,
                "show_courses_section" boolean NOT NULL DEFAULT 1,
                "button_text" varchar(50) NOT NULL DEFAULT 'View All Courses',
                "is_active" boolean NOT NULL DEFAULT 1
            )
        """)
    except Exception as e:
        print(f"Error creating tables: {e}")
        # Tables might already exist, which is fine
        pass

def reverse_func(apps, schema_editor):
    pass  # We don't want to delete the tables on reverse migration

class Migration(migrations.Migration):
    dependencies = [
        ('pages', '0005_aboutcourses_aboutme_abouttuition'),
    ]

    operations = [
        migrations.RunPython(forwards_func, reverse_func),
    ]
    