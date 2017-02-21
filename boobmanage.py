#!/usr/bin/env python

from weboob.core import Weboob
from weboob.exceptions import ModuleLoadError
from weboob.core.backendscfg import BackendAlreadyExists
import logging

logger = logging.getLogger(__name__)


class Boobmanage:
    """ Class that performs management of needed backend """

    def __init__(self):
        self.weboob = Weboob()

    def has_backend(self, backend):
        logger.debug("has_backend(): backend: %s" % backend)
        for backend_name, module_name, params in sorted(
                self.weboob.backends_config.iter_backends()):
            logger.debug('has_backend(): checking module "%r"' % module_name)
            try:
                self.weboob.modules_loader.get_or_load_module(
                        module_name)
            except ModuleLoadError as e:
                self.logger.warning('has_backend(): unable to load module '
                                    '"%r": %s' % (module_name, e))
                continue
            if backend == backend_name:
                logger.debug('has_backend(): backend "%s" found, returning'
                             ' True' % backend)
                return True
            logger.debug("has_backend(): looping to the next module")
        logger.debug('has_backend(): backend "%s" not found, returning'
                     ' False' % backend)
        return False

    def add_backend(self, backend, params):
        logger.debug("add_backend(): backend: %s | params: %s" %
                     (backend, params))
        minfo = self.weboob.repositories.get_module_info(backend)
        config = None
        module = None

        try:
            if minfo is None:
                raise ModuleLoadError(backend, "Module for backend "
                                      "%s does not exist" % backend)
            logger.debug('add_backend(): module for backend "%s" loaded'
                         % (backend))
            if not minfo.is_installed():
                logger.warning('add_backend(): module "%s" is available but '
                               'not installed' % minfo.name)
            else:
                logger.debug('add_backend(): module "%s" is installed'
                             % minfo.name)
            module = self.weboob.modules_loader.get_or_load_module(backend)
            config = module.config

        except ModuleLoadError as e:
            logger.error('add_backend(): unable to load module "%s": %s'
                         % (backend, e))
            return False

        try:

            config = config.load(self.weboob, module.name, backend, params,
                                 nofail=True)

            for key, value in params.iteritems():
                if key not in config:
                    logger.debug('add_backend(): config named "%s" is not '
                                 'known for the module "%s", ignoring'
                                 % (key, backend))
                    continue
                logger.debug('add_backend(): config named "%s" loaded in '
                             'module "%s"' % (key, backend))
                config[key].set(value)

            config.save(edit=False)
            logger.debug('add_backend(): backend "%s" loaded and configured, '
                         'returning True' % backend)
            return True
        except BackendAlreadyExists:
            logger.warning('add_backend(): backend "%s" already exists, doing'
                           ' nothing' % backend)
            return True
