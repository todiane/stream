from django.shortcuts import render, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.http import Http404
from .models import Page, Hero
from courses.models import Course
from .models import HeroBanner, AboutMe, AboutTuition, AboutCourses


def home_view(request):
    try:
        page = Page.objects.get(template='home', is_active=True)
        hero = Hero.objects.filter(is_active=True).first()
        banner = HeroBanner.objects.filter(is_active=True).first()
        featured_courses = Course.objects.filter(status='publish')[:6]
        
        context = {
            'page': page,
            'hero': hero,
            'banner': banner,
            'object_list': featured_courses,
            'meta_description': 'GCSE English Language and Literature - online courses and tuition', 
            'meta_title': 'Stream English - GCSE English Language and Literature tuition' 
        }
        return render(request, 'pages/home.html', context)
    except Page.DoesNotExist:
        raise Http404("Homepage not found")
    

def about_view(request):
    try:
        page = get_object_or_404(Page, template='about', is_active=True)
        about_me = AboutMe.objects.filter(is_active=True).first()
        tuition = AboutTuition.objects.filter(is_active=True).first()
        courses_section = AboutCourses.objects.filter(is_active=True).first()
        featured_courses = Course.objects.filter(status='publish')[:6] if courses_section and courses_section.show_courses_section else None
        
        context = {
            'page': page,
            'about_me': about_me,
            'tuition': tuition,
            'courses_section': courses_section,
            'object_list': featured_courses,
            'meta_description': 'About Stream English - GCSE English Language and Literature tuition', 
            'meta_title': 'About GCSE English tuition with Robyn Wear of Stream English' 
        }
        return render(request, 'pages/about.html', context)
    except Exception as e:
        print(f"Error in about_view: {e}")
        # Return a basic context if data is missing
        return render(request, 'pages/about.html', {
            'page': page if 'page' in locals() else None
        })

@staff_member_required
def preview_page(request, pk):
    page = get_object_or_404(Page, pk=pk)
    hero = Hero.objects.filter(is_active=True).first() if page.template == 'home' else None
    featured_courses = Course.objects.filter(status='publish')[:6] if page.template == 'home' else None
    
    context = {
        'page': page,
        'hero': hero,
        'object_list': featured_courses,
        'is_preview': True
    }
    template = f'pages/{page.template}.html'
    return render(request, template, context)
