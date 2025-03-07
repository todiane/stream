# Stream English EduCommerce

Stream English is an educational platform focused on English Language and Literature lessons and tutoring. 

It has been built with a modern tech stack and following best practices for web development. The site contains a learning management system, where YouTube videos are uploaded. There is also a shop that provides the ability to add digital products. Stripe is used for taking payment. Finally, there is a blog/news site where articles and videos can be added to help promote the platform.

It is a comprehensive Django-based platform for online English courses with integrated e-commerce functionality.

## Project Overview

Stream English (https://streamenglish.co.uk) is an educational platform built with Django that provides:

- Online English courses with video lessons
- Student progress tracking
- Digital product downloads (worksheets, guides, etc.)
- Secure user authentication and profiles
- Integrated e-commerce with Stripe payments

## System Requirements

- Python 3.8+
- Django 4.x
- MySQL/MariaDB
- Node.js (for frontend assets)

## Project Structure

```
stream/
├── courses/                  # Course and lesson management
│   ├── models.py             # Course and Lesson models
│   ├── services.py           # Business logic for courses
│   ├── urls.py               # URL routing for courses
│   ├── utils.py              # Utility functions
│   └── views.py              # Course and lesson views
│
├── profiles/                 # User profiles and progress tracking
│   ├── middleware.py         # IP rate limiting
│   ├── models.py             # Profile and VideoProgress models
│   ├── tokens.py             # User authentication tokens
│   ├── urls.py               # URL routing for profiles
│   └── views.py              # Profile views
│
├── shop/                     # E-commerce functionality
│   ├── cart.py               # Shopping cart implementation
│   ├── emails.py             # Order emails
│   ├── models.py             # Product and Order models
│   └── views.py              # Shop views
│
├── news/                     # News and blog functionality
│   ├── models.py             # Post and Category models
│   └── views.py              # News views
│
├── pages/                    # Static pages
│
├── stream/                   # Core project files
│   ├── middleware/           # Custom middleware
│   ├── settings.py           # Project settings
│   ├── sitemaps.py           # SEO sitemaps
│   ├── storage.py            # Custom storage backends
│   ├── urls.py               # Project URL configuration
│   ├── utils.py              # Core utility functions
│   └── views.py              # Core views
│
├── static/                   # Static files (CSS, JS, images)
│   └── js/
│       └── video-tracking.js # Video progress tracking
│
├── templates/                # HTML templates
│   ├── base.html             # Base template
│   ├── courses/              # Course templates
│   ├── profiles/             # Profile templates
│   └── shop/                 # Shop templates
│
├── media/                    # User-uploaded files
│   ├── public/               # Publicly accessible files
│   └── secure_downloads/     # Protected downloadable files
│
└── logs/                     # Application logs
```

## Key Features

### Video Progress Tracking

The platform tracks user progress through video lessons, allowing students to resume where they left off. Progress is saved to the database via AJAX requests.

Key components:
- JavaScript tracking (static/js/video-tracking.js)
- VideoProgress model (profiles/models.py)
- AJAX endpoints (profiles/views.py)

### Course and Lesson Management

Admin users can create and manage courses and lessons, including:
- Course information and descriptions
- Video lessons with YouTube embeds or uploaded files
- Course enrollment and student progress tracking

### User Profiles

- User registration and authentication
- Email verification
- Profile management
- Progress tracking
- Enrollment in courses

### E-commerce

- Digital product sales
- Secure checkout with Stripe
- Order management
- Download tracking
- Product reviews

## Development Setup

1. Clone the repository
2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Create a `.env` file with required environment variables (see .env.example)
5. Run migrations:
   ```
   python manage.py migrate
   ```
6. Create a superuser:
   ```
   python manage.py createsuperuser
   ```
7. Run the development server:
   ```
   python manage.py runserver
   ```

## Production Deployment

The site is deployed on WebHostUK's cPanel Django hosting with MariaDB.

### Deployment Checklist

- Set `DEBUG = False` in settings.py
- Configure proper ALLOWED_HOSTS
- Ensure all static files are collected
- Set up proper email configuration
- Configure Stripe keys for production
- Set strong SECRET_KEY
- Enable HTTPS/SSL

### Server Configuration

- Web server: Apache with mod_wsgi
- Database: MariaDB
- Media storage: Local filesystem
- Email: SMTP via cPanel

## License

Proprietary - All rights reserved

# Developer

Diane Corriette
https://www.djangify.com 

Stream English
https://djangify.com/portfolio/stream-english/ 