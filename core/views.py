from django.shortcuts import render

# Create your views here.

def index(request):
    # Use the render function to return an HTTP response
    return render(request, 'index.html', {})
