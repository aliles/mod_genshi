"""WSGI application class for mod_genshi
"""
import mimetypes
import os

from genshi.template import TemplateLoader, TemplateNotFound

__all__ = ['WSGI']


class WSGI(object):
    """mod_genshi WSGI application."""

    def __init__(self):
        self.loader = TemplateLoader(os.path.abspath(os.curdir),
            auto_reload=True)
        self.index = 'index.html'

    def _get_path(self, environ):
        "Translate request path to template path"
        path = environ['PATH_INFO']
        if path.startswith('/'):
            path = path[:1]
        if path.endswith('/'):
            path += self.index
        return path

    def _headers(self, environ):
        "Build HTTP response headers, guessing the content type"
        content_type, encoding = mimetypes.guess_type(self._get_path(environ))
        headers = [('Content-Type', content_type)]
        if encoding is not None:
            headers.append(('Content-Encoding', encoding))
        return headers

    def _body(self, environ):
        "Generate response body from Genshi template"
        path = environ['PATH_INFO']
        if path.startswith('/'):
            path = path[1:]
        if path.endswith('/'):
            path += self.index
        template = self.loader.load(path)
        stream = template.generate(ENVIRON=environ)
        return stream.render()

    def request(self, environ, start_response):
        "Serve a HTTP request"
        try:
            body = [self._body(environ)]
            status = '200 OK'
            response_headers = self._headers(environ)
        except TemplateNotFound:
            body = ['Page Not Found']
            status = '400 Not Found'
            response_headers = [('Content-Type', 'text/plain')]
        start_response(status, response_headers)
        return body

    __call__ = request
