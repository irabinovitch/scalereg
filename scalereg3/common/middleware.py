"""Project-specific middleware helpers."""

import logging


logger = logging.getLogger('django.request')


class AdminHostLoggingMiddleware:
    """Log the host header for admin requests to debug preview proxies."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/admin'):
            host_header = request.META.get('HTTP_HOST', '<missing>')
            try:
                resolved_host = request.get_host()
            except Exception as exc:  # pragma: no cover - diagnostic logging
                resolved_host = f'<error: {exc}>'
            logger.info('Admin request host header=%s resolved_host=%s',
                        host_header, resolved_host)
        return self.get_response(request)
