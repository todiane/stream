from django.shortcuts import render
from courses import services 

app_name = 'stream'


def home_view(request, *args, **kwargs):
    queryset = services.get_publish_courses()
    context = {
        "object_list": queryset[:3]  # Get first 3 published courses
    }
    template_name = "home.html"
    return render(request, template_name, context)


from courses import services

def about_view(request):
    queryset = services.get_publish_courses()
    context = {
        "object_list": queryset
    }
    template_name = "about.html"
    return render(request, template_name, context)

def privacy_view(request):
    template_name = "policy/privacy.html"
    return render(request, template_name)  

def terms_view(request):
    template_name = "policy/terms-conditions.html"
    return render(request, template_name)  
