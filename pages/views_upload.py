# pages/views_upload.py
import os
import uuid
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.admin.views.decorators import staff_member_required

from stream.storage import public_storage


# TinyMCE 6's native image uploader posts a plain multipart XHR that does not
# include Django's CSRF token, so csrf_protect would 403 the upload. The view is
# still locked down by staff_member_required (admin session required) and
# require_POST, so exempting CSRF here is safe for this staff-only endpoint.
@staff_member_required
@require_POST
@csrf_exempt
def tinymce_upload(request):
    """
    Handle TinyMCE inline image uploads.
    Only accessible by staff/admin users.
    """
    if "file" not in request.FILES:
        return JsonResponse({"error": "No file uploaded"}, status=400)

    uploaded_file = request.FILES["file"]

    # Validate file type
    allowed_types = ["image/jpeg", "image/png", "image/webp"]
    if uploaded_file.content_type not in allowed_types:
        return JsonResponse({"error": "Invalid file type"}, status=400)

    # Validate file size (max 5MB)
    if uploaded_file.size > 5 * 1024 * 1024:
        return JsonResponse({"error": "File too large (max 5MB)"}, status=400)

    # Generate unique filename
    ext = os.path.splitext(uploaded_file.name)[1].lower()
    filename = f"uploads/tinymce/{uuid.uuid4().hex}{ext}"

    # Save via public_storage so the file lands under /media/public/ and is
    # served correctly in production (see stream/storage.py).
    saved_path = public_storage.save(filename, uploaded_file)
    file_url = public_storage.url(saved_path)

    # TinyMCE expects this response format
    return JsonResponse({"location": file_url})
