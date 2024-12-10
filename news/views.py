# news/views.py

from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator

from stream import settings
from .models import Post, Category
from django.utils import timezone




def news_list(request):
    print("news_list view called")  # Debugging line
    posts = Post.objects.filter(
        status='published',
        publish_date__lte=timezone.now()
    ).select_related('category')
    
    paginator = Paginator(posts, 12)
    page = request.GET.get('page')
    posts = paginator.get_page(page)
    
    print(f"Number of posts: {posts.paginator.count}")  # Debugging line
    
    context = {
        'posts': posts,
        'categories': Category.objects.all(),
        'title': 'News',
        'meta_description': 'Latest news and updates from Stream English',
        'debug': settings.DEBUG,  # Add this line
    }
    return render(request, 'news/list.html', context)

def category_list(request, slug):
    print(f"\nCategory view called with slug: {slug}")  # Debug print
    
    category = get_object_or_404(Category, slug=slug)
    posts = Post.objects.filter(
        category=category,
        status='published',
        publish_date__lte=timezone.now()
    ).order_by('-publish_date')  # Add explicit ordering
    
    print(f"Posts queryset count: {posts.count()}")  # Debug print
    for post in posts:
        print(f"- {post.title} (Status: {post.status}, Date: {post.publish_date})")  # Debug print
    
    paginator = Paginator(posts, 12)
    page = request.GET.get('page')
    posts = paginator.get_page(page)
    
    context = {
        'category': category,
        'posts': posts,
        'categories': Category.objects.all(),
        'title': f'{category.name} - News',
        'meta_description': f'Latest news and updates about {category.name} from Stream English',
    }
    
    print(f"Posts in context: {[p.title for p in context['posts']]}")  # Debug print
    
    return render(request, 'news/category.html', context)


def post_detail(request, slug):
    post = get_object_or_404(Post, 
        slug=slug,
        status='published',
        publish_date__lte=timezone.now()
    )
    
    # Get next and previous posts
    next_post = Post.objects.filter(
        status='published',
        publish_date__lte=timezone.now(),
        publish_date__gt=post.publish_date
    ).order_by('publish_date').first()

    previous_post = Post.objects.filter(
        status='published',
        publish_date__lte=timezone.now(),
        publish_date__lt=post.publish_date
    ).order_by('-publish_date').first()
    
    latest_posts = Post.objects.filter(
        status='published',
        publish_date__lte=timezone.now()
    ).exclude(id=post.id)[:5]
    
    context = {
        'post': post,
        'next_post': next_post,
        'previous_post': previous_post,
        'latest_posts': latest_posts,
        'categories': Category.objects.all(),
        'title': post.meta_title or post.title,
        'meta_description': post.meta_description,
        'meta_keywords': post.meta_keywords,
    }
    return render(request, 'news/detail.html', context)