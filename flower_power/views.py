from django.core.files.storage import default_storage
from django.db import connection, DatabaseError
from django.http import FileResponse, Http404, JsonResponse
from django.views.decorators.http import require_safe


@require_safe
def health(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
    except DatabaseError:
        return JsonResponse({'status': 'unavailable'}, status=503)
    return JsonResponse({'status': 'ok'})


@require_safe
def product_image(request, filename):
    """Serve only uploaded product photos, never arbitrary filesystem paths."""
    from shop.models import Product
    if not Product.objects.filter(image=filename).exists():
        raise Http404
    try:
        response = FileResponse(default_storage.open(filename, 'rb'))
    except (FileNotFoundError, ValueError):
        raise Http404
    response['X-Content-Type-Options'] = 'nosniff'
    response['Cache-Control'] = 'public, max-age=3600'
    return response
