"""WSGI application class for mod_genshi
"""
import mimetypes
import os
import re

from genshi.template import TemplateLoader, TemplateNotFound, TemplateError
from genshi.template import MarkupTemplate, NewTextTemplate
from webob import Request, Response
from webob.exc import HTTPNotFound, HTTPForbidden, HTTPError, HTTPServerError
from webob.static import DirectoryApp

from mod_genshi import configuration

__all__ = ['WSGI']


class WSGI(object):
    """mod_genshi WSGI application."""

    def __init__(self):
        self.config = configuration.Config()
        self.static = DirectoryApp(self.config.staticdir)
        self.loader = TemplateLoader(self.config.templatedir,
                                     auto_reload=True)

    def _is_path_blocked(self, basepath, relpath):
        "Raise HTTPForbidden if path is blocked"
        if relpath.endswith(self.config.suffix_blocked):
            raise HTTPForbidden(comment=relpath)
        _, filename = os.path.split(relpath)
        if filename.startswith('.'):
            raise HTTPForbidden(comment=relpath)
        abspath = os.path.join(basepath, relpath)
        realpath = os.path.realpath(abspath)
        prefix = os.path.commonprefix((realpath, basepath))
        if prefix != basepath:
            raise HTTPForbidden(comment=relpath)

    def _is_static_path_blocked(self, path):
        self._is_path_blocked(self.config.staticdir, path)
        if not path.endswith(self.config.suffix_static):
            raise HTTPForbidden(comment=path)

    def _is_template_path_blocked(self, path):
        self._is_path_blocked(self.config.templatedir, path)

    def _get_basic_path(self, url):
        "Translate request path to template path"
        path = re.sub(r'/{2,}', r'/', url)
        if path.startswith('/'):
            path = path[1:]
        if path.endswith('/') or path == '':
            path += self.config.index
        return path

    def _get_template_style(self, path):
        "Return class for template type"
        if path.endswith(self.config.suffix_markup):
            return MarkupTemplate
        elif path.endswith(self.config.suffix_text):
            return NewTextTemplate
        return None

    def _headers(self, template, response):
        "Populate '200 OK' HTTP response, guessing the content type"
        content_type, encoding = mimetypes.guess_type(template)
        if encoding is not None:
            response.content_encoding = encoding
        if content_type is None:
            content_type = self.config.default_content_type
        response.content_type = content_type
        response.status_code = 200

    def _body(self, path, style, request, response):
        "Generate response body from Genshi template"
        template = self.loader.load(path, cls=style)
        stream = template.generate(REQUEST=request, RESPONSE=response)
        response.body = stream.render()

    def __call__(self, environ, start_response):
        "Serve a HTTP request"
        request = Request(environ)
        response = Response()
        try:
            path = self._get_basic_path(request.path)
            style = self._get_template_style(request.path)
            if style:
                self._is_template_path_blocked(path)
                self._headers(path, response)
                self._body(path, style, request, response)
            else:
                self._is_static_path_blocked(path)
                response = request.get_response(self.static)
        except TemplateNotFound:
            response = HTTPNotFound(comment=request.path)
        except TemplateError:
            response = HTTPServerError(comment=request.path)
        except HTTPError as err:
            response = err
        return response(environ, start_response)
