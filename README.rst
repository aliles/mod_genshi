mod_genshi
==========

**PHP like web framework based on Genshi**

Motivation
----------
`PHP <http://www.php.net/>`_ has a reputation for
`questionable language design <http://me.veekun.com/blog/2012/04/09/php-a-fractal-of-bad-design/>`_.
It does however have one outstanding feature,
the ease with which someone can get started.
It has excellent server support.
To get started with PHP
someone just needs to edit a file on disk
and point a web browser towards it.

`I thought it would be amusing <https://twitter.com/#!/aliles/status/192573400613527552>`_
to try and emulate this behaviour with Python.
Thus *mod_genshi* was born.
It's built using the `Genshi <http://genshi.edgewall.org/>`_
templating package.
Genshi was chosen ahead of
`Mako <http://www.makotemplates.org/>`_
or `Jinja2 <http://jinja.pocoo.org/docs/>`_
as Genshi supports arbitrary Python blocks.

Warning
-------
**You (probably) DO NOT want to use mod_genshi.**
There is a HUGE number of web frameworks written in Python.
Some notable projects include:

* `Django <https://www.djangoproject.com/>`_
* `Bottle <http://bottlepy.org/docs/dev/>`_
* `Flask <http://flask.pocoo.org/>`_
* `Pylons <http://docs.pylonsproject.org/en/latest/index.html>`_
* `Turbogears <http://turbogears.org/>`_

This is just a small sample
of the current state of Python web frameworks.
Please look around
before deciding to use *mod_genshi*.

Status
------
*mod_genshi* is very immature
and NOT ready for production use.
A shortened list of features
that are still to be completed.

* Use `WebOb <http://www.webob.org/>`_ to manage request and response objects.
* Load configuration from config file.
* Extend Python path for templates from configuration.
* Enables templates to change response code and headers.
* Allow multiple application instances to co-exist.

Not to mention all the documentation that is required.

|build_status|

Usage
-----
The *mod_genshi* WSGI application
will load and render templates
relative to the servers working directory.

development
```````````
*mod_genshi* includes a HTTP server
based on the wsgiref module.
It is only suitable for development.
To use this development server. ::

	$ python -m mod_genshi.server

This will run the *mod_genshi* development server
on port 8000.
The port can be changed
by passing a different port number
as the first command line argument.

gunicorn
````````
`gunicorn <http://gunicorn.org/>`_ is popular WSGI server.
To run *mod_genshi* using gunicorn. ::

	$ gunicorn mod_genshi.app:handler

See the gunicorn documentation
for details on configuration.

.. |build_status| image:: https://secure.travis-ci.org/aliles/mod_genshi.png?branch=master
   :target: http://travis-ci.org/#!/aliles/mod_genshi
