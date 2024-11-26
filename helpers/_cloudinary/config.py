import cloudinary
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

def cloudinary_init():   
    if not all([settings.CLOUDINARY_CLOUD_NAME, 
                settings.CLOUDINARY_API_KEY, 
                settings.CLOUDINARY_API_SECRET]):
        raise ImproperlyConfigured(
            'Cloudinary settings CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, '
            'and CLOUDINARY_API_SECRET must be set in your settings.'
        )
    
    cloudinary.config( 
        cloud_name = settings.CLOUDINARY_CLOUD_NAME, 
        api_key = settings.CLOUDINARY_API_KEY, 
        api_secret = settings.CLOUDINARY_API_SECRET,
        secure=True
    )
    