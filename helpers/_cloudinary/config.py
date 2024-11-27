import cloudinary
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

def cloudinary_init():
    """Initialize cloudinary configuration"""
    if not all([settings.CLOUDINARY_STORAGE['CLOUD_NAME'], 
                settings.CLOUDINARY_STORAGE['API_KEY'], 
                settings.CLOUDINARY_STORAGE['API_SECRET']]):
        raise ImproperlyConfigured(
            'Cloudinary settings CLOUD_NAME, API_KEY, and API_SECRET '
            'must be set in your CLOUDINARY_STORAGE settings.'
        )
    
    cloudinary.config( 
        cloud_name=settings.CLOUDINARY_STORAGE['CLOUD_NAME'],
        api_key=settings.CLOUDINARY_STORAGE['API_KEY'],
        api_secret=settings.CLOUDINARY_STORAGE['API_SECRET'],
        secure=True
    )
    return True
