# pages/views.py
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.http import Http404
from .models import Page, Hero, TuitionFeature
from shop.models import Product
from courses.models import Course
from .models import HeroBanner, AboutFeature


def home_view(request):
    try:
        page = Page.objects.get(template="home", is_active=True)
        hero = Hero.objects.filter(is_active=True).first()
        banner = HeroBanner.objects.filter(is_active=True).first()
        featured_courses = Course.objects.filter(status="publish")[:3]

        featured_products = Product.objects.filter(
            featured=True, status="publish", is_active=True
        ).order_by("created")[:3]

        context = {
            "page": page,
            "hero": hero,
            "banner": banner,
            "object_list": featured_courses,
            "meta_description": "GCSE English Language and Literature - online courses and tuition",
            "featured_products": featured_products,
            "meta_title": "Stream English - GCSE English Language and Literature tuition",
        }
        return render(request, "pages/home.html", context)
    except Page.DoesNotExist:
        raise Http404("Homepage not found")


def page_detail_view(request, slug):
    page = get_object_or_404(Page, slug=slug, is_active=True)

    # Redirect to appropriate view based on template
    if page.template == "home":
        return redirect("pages:home")
    elif page.template == "about":
        return redirect("pages:about")
    elif page.template == "tuition":
        return redirect("pages:tuition")

    context = {
        "page": page,
    }
    return render(request, f"pages/{page.template}.html", context)


def about_view(request):
    try:
        page = get_object_or_404(Page, template="about", is_active=True)
        features = AboutFeature.objects.filter(is_active=True).order_by("order")
        featured_courses = Course.objects.filter(status="publish")[:3]

        context = {
            "page": page,
            "features": features,
            "object_list": featured_courses,
            "meta_description": "About Stream English - GCSE English Language and Literature tuition",
            "meta_title": "About GCSE English tuition with Stream English",
        }
        return render(request, "pages/about.html", context)
    except Exception as e:
        print(f"Error in about_view: {e}")
        return render(
            request, "pages/about.html", {"page": page if "page" in locals() else None}
        )


@staff_member_required
def preview_page(request, pk):
    page = get_object_or_404(Page, pk=pk)
    hero = (
        Hero.objects.filter(is_active=True).first() if page.template == "home" else None
    )
    featured_courses = (
        Course.objects.filter(status="publish")[:6] if page.template == "home" else None
    )

    context = {
        "page": page,
        "hero": hero,
        "object_list": featured_courses,
        "is_preview": True,
    }
    template = f"pages/{page.template}.html"
    return render(request, template, context)


def tuition_view(request):
    try:
        page = get_object_or_404(Page, template="tuition", is_active=True)
        features = TuitionFeature.objects.filter(is_active=True).order_by("order")

        # Add this to get featured products from shop
        featured_products = Product.objects.filter(
            featured=True,
            status="publish",
            is_active=True,
            product_type="tuition",
        ).order_by("created")[:3]

        context = {
            "page": page,
            "features": features,
            "featured_products": featured_products,  # Add this to context
        }
        return render(request, "pages/tuition.html", context)
    except Exception as e:
        print(f"Error in tuition_view: {e}")
        return render(
            request,
            "pages/tuition.html",
            {"page": page if "page" in locals() else None},
        )
