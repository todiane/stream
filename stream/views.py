from django.shortcuts import render


def home_view(request, *args, **kwargs):
    template_name = "home.html"
    return render(request, template_name) 


def about_view(request):
    template_name = "about.html"
    return render(request, template_name)  

def privacy_view(request):
    template_name = "policy/privacy.html"
    return render(request, template_name)  

def terms_view(request):
    template_name = "policy/terms-conditions.html"
    return render(request, template_name)  
