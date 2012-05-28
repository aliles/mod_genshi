"""PEP 302 import hook to reload modules on changes.

Implements an import hook using a finder and a loader class to load modules
from a filesystem path using the existing imp module. The modification time of
all Python source files are recorded. The modifiation times can then be used
later to generate a list of modified modules, unload modified modules or unload
all modules if any are modified.

To use, call the register classmethod on ReloadingFinder. This method is
indempotent. Calling this method will register a token at the end of sys.path
to initiate imports from the path location.
"""
from collections import defaultdict, namedtuple
import imp
import os
import random
import string
import sys


# containers for common data sets
Location = namedtuple('Location', 'fobject pathname description')
Source = namedtuple('Source', 'pathname mtime')


class ReloadingLoader(object):
    """Import hook loader.

    Used by the ReloadingFinder class. Implemented using the imp module.
    """

    def __init__(self, source, token):
        self.source = source
        self.token = token

    def load_module(self, fullname):
        "Import hook protocol."
        try:
            module = imp.load_module(fullname, *self.source)
            if hasattr(module, '__path__'):
                module.__path__ = [self.token + self.source.pathname]
            return module
        finally:
            if hasattr(self.source.fobject, 'close'):
                self.source.fobject.close()


class ReloadingFinder(object):
    """Import hook loader.

    Finds modules using the imp module. Records the modification time for
    module source files. The default search path for modules is empty by
    default. This can be over ridden by passing a iterable of paths name when
    creating the instance.

    Instances have the following properties.

     - loaded
     - modified

    With the names of modules that have been loaded and modified since loaded.
    Deleting this properties unloads the modules. Instances also have an
    ismodified property that is True if there are modified modules.

    To create a ReloadingFinder, use the register class method. This will
    return a new instance of ReloadingFinder after adding a token to sys.path.
    Use the unregister class method to reverse this.
    """

    MTIMES = defaultdict(dict)
    PATHS = {}
    TOKENS = {}

    TOKEN_LEN = 40

    def __init__(self, index):
        try:
            suffix = index[self.TOKEN_LEN:]
            self._token = index[:self.TOKEN_LEN]
            self._path = [self.PATHS[self._token]]
            if suffix:
                self._path = [suffix]
            self._mtimes = self.MTIMES[self._token]
        except KeyError:
            raise ImportError

    @classmethod
    def register(cls, path):
        "Create a new reloading path"
        if path not in cls.TOKENS:
            token = "".join(random.choice(string.letters)
                            for i in range(cls.TOKEN_LEN))
            cls.TOKENS[path] = token
            cls.PATHS[token] = path
            sys.path.append(token)
        token = cls.TOKENS[path]
        return cls(cls.TOKENS[path])

    @classmethod
    def unregister(cls, path):
        "Remove an existing reloading path"
        if path not in cls.TOKENS:
            return
        token = cls.TOKENS[path]
        del cls.TOKENS[path]
        del cls.PATHS[token]
        sys.path.remove(token)

    @property
    def ismodified(self):
        for _ in self._iter_modified():
            return True
        return False

    @property
    def loaded(self):
        return list(self._mtimes.keys())

    @loaded.deleter
    def loaded(self):
        for fullname in self.loaded:
            del sys.modules[fullname]
            del self._mtimes[fullname]

    @property
    def modified(self):
        return [module for module in self._iter_modified()]

    @modified.deleter
    def modified(self):
        for fullname in self.modified:
            del sys.modules[fullname]
            del self._mtimes[fullname]

    def _find_location(self, module, path):
        fobject, pathname, description = imp.find_module(module, path)
        location = Location(fobject, pathname, description)
        return location

    def _iter_modified(self):
        for fullname in self._mtimes:
            location = self._mtimes[fullname]
            mtime = os.path.getmtime(location.pathname)
            if mtime != location.mtime:
                yield fullname

    def _module_name(self, fullname):
        hierarchy = fullname.rsplit('.', 1)
        return hierarchy[-1]

    def _record_mtime(self, fullname, location):
        mtime = os.path.getmtime(location.pathname)
        source = Source(location.pathname, mtime)
        self._mtimes[fullname] = source

    def clear(self):
        "Unload all imported modules"
        del self.loaded

    def find_module(self, fullname):
        "Import hook protocol."
        try:
            module = self._module_name(fullname)
            location = self._find_location(module, self._path)
            self._record_mtime(fullname, location)
            return ReloadingLoader(location, self._token)
        except ImportError:
            pass


sys.path_hooks.append(ReloadingFinder)

register = ReloadingFinder.register
unregister = ReloadingFinder.unregister
