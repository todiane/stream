import cloudinary
from django.conf import settings
from django.template.loader import get_template
from django.core.exceptions import ImproperlyConfigured

def get_cloudinary_image_object(instance=None, field_name=None, width=None, height=None, format=None, as_html=False):
    """Get a Cloudinary image URL or HTML with optional transformations"""
    if not instance or not field_name:
        return None
    
    if not hasattr(instance, field_name):
        return None
        
    field_value = getattr(instance, field_name)
    if not field_value:
        return None

    try:
        options = {}
        if width:
            options['width'] = width
        if height:
            options['height'] = height
        if format:
            options['format'] = format

        if as_html:
            return field_value.image(**options)
        
        return field_value.build_url(**options)
    except Exception as e:
        print(f"Error getting cloudinary image: {e}")
        return None

def get_cloudinary_video_object(instance, 
                              field_name="video",
                              as_html=False,
                              width=None,
                              height=None,
                              sign_url=True,
                              fetch_format="auto",
                              quality="auto",
                              controls=True,
                              autoplay=True):
    if not hasattr(instance, field_name):
         return ""
    video_object = getattr(instance, field_name)
    if not video_object:
        return ""
    video_options = {
        "sign_url": sign_url,
        "fetch_format": fetch_format,
        "quality": quality,
        "controls": controls,
        "autoplay": False,
    }
    if width is not None:
        video_options['width'] = width
    if height is not None:
        video_options['height'] = height
    if height and width:
        video_options['crop'] = "limit"
    url = video_object.build_url(**video_options)
    if as_html:
        template_name = "videos/snippets/embed.html"
        tmpl = get_template(template_name)
        cloud_name = settings.CLOUDINARY_CLOUD_NAME
        _html = tmpl.render({
            'video_url': url, 
            'cloud_name': cloud_name, 
            'base_color': "#007cae"
        })
        return _html
    return url

def cloudinary_init():   
    if not all([
        settings.CLOUDINARY_CLOUD_NAME, 
        settings.CLOUDINARY_API_KEY, 
        settings.CLOUDINARY_API_SECRET
    ]):
        raise ImproperlyConfigured(
            'Cloudinary settings CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, '
            'and CLOUDINARY_API_SECRET must be set in your settings.'
        )
    
    cloudinary.config( 
        cloud_name=settings.CLOUDINARY_CLOUD_NAME, 
        api_key=settings.CLOUDINARY_API_KEY, 
        api_secret=settings.CLOUDINARY_API_SECRET,
        secure=True
    )