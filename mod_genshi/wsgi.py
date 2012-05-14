"""WSGI application class for mod_genshi
"""
import mimetypes
import os
import re

from genshi.template import TemplateLoader, TemplateNotFound
from webob import Request, Response
from webob.exc import HTTPNotFound, HTTPForbidden, HTTPError

__all__ = ['WSGI']


class WSGI(object):
    """mod_genshi WSGI application."""

    def __init__(self):
        self.blocked_suffixes = ('.swp', '.bak', '~')
        self.index = 'index.html'
        self.templatedir = os.path.abspath(os.curdir)
        self.loader = TemplateLoader(self.templatedir, auto_reload=True)

    def _is_path_blocked(self, relpath):
        "Raise HTTPForbidden if path is blocked"
        if relpath.endswith(self.blocked_suffixes):
            raise HTTPForbidden()
        abspath = os.path.join(self.templatedir, relpath)
        realpath = os.path.realpath(abspath)
        prefix = os.path.commonprefix((realpath, self.templatedir))
        if prefix != self.templatedir:
            raise HTTPForbidden()
        return relpath

    def _get_template_path(self, url):
        "Translate request path to template path"
        if '..' in url:
            raise HTTPForbidden()
        path = re.sub(r'/{2,}', r'/', url)
        if path.startswith('/'):
            path = path[1:]
        if path.endswith('/') or path == '':
            path += self.index
        self._is_path_blocked(path)
        return path

    def _headers(self, template, response):
        "Populate '200 OK' HTTP response, guessing the content type"
        content_type, encoding = mimetypes.guess_type(template)
        if encoding is not None:
            response.content_encoding = encoding
        if content_type is None:
            content_type = 'text/plain'
        response.content_type = content_type
        response.status_code = 200

    def _body(self, path, request, response):
        "Generate response body from Genshi template"
        template = self.loader.load(path)
        stream = template.generate(REQUEST=request, RESPONSE=response)
        response.body = stream.render()

    def __call__(self, environ, start_response):
        "Serve a HTTP request"
        request = Request(environ)
        response = Response()
        try:
            template = self._get_template_path(request.path)
            self._headers(template, response)
            self._body(template, request, response)
        except TemplateNotFound:
            response = HTTPNotFound()
        except HTTPError as err:
            response = err
        return response(environ, start_response)
