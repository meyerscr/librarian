"""
setup.py: Device specific librarian configuration

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import collections
import json
import logging
import os

from bottle import request

from ..core.contrib.templates.renderer import template
from ..core.exts import ext_container as exts
from ..presentation.wizard import Wizard


class Setup(object):
    """
    Provides access to data generated by the setup wizard and facilities for
    writing such data into the setup file.

    Automatic configuration is applied every time the setup file is found to be
    empty. Functions registered for auto configuration will be applied in the
    same order they were registered.
    """
    _auto_configurators = collections.OrderedDict()

    def __init__(self, path):
        self._setup_file = os.path.abspath(path)
        self._data = dict()

    def __getitem__(self, key):
        return self._data[key]

    def __contains__(self, key):
        return key in self._data

    def get(self, key, default=None):
        return self._data.get(key, default)

    def items(self):
        return self._data.items()

    def append(self, new_data):
        """
        Update the underlying data structure storing the setup data with the
        passed in ``new_data``, save the updated structure in the setup file,
        and update the global configuration with the freshly updated data.
        """
        self._data.update(new_data)
        with open(self._setup_file, 'w') as s_file:
            json.dump(self._data, s_file)

        self._update_config()

    def _update_config(self):
        """
        Update the global configuration with the current setup data.
        """
        exts.config.update(self._data)

    def _read(self):
        """
        Attempt loading the setup data file.
        """
        if os.path.exists(self._setup_file):
            try:
                with open(self._setup_file, 'r') as s_file:
                    self._data = json.load(s_file)
            except Exception as exc:
                msg = 'Setup file loading failed: {0}'.format(str(exc))
                logging.error(msg)

    def _auto_configure(self):
        """
        Execute configuration options which can be applied automatically.
        """
        data = dict((key, config_fn())
                    for (key, config_fn) in self._auto_configurators.items())
        self.append(data)

    def load(self):
        """
        Read setup data from file and update the global configuration with the
        data obtained from it. In case the setup file returned no data, run the
        registered auto configurators.
        """
        self._read()
        if not self._data:
            self._auto_configure()
        self._update_config()

    @classmethod
    def autoconfigure(cls, key, fn):
        """
        Register a function that performs automatic configuration (returning a
        value), that will be added to the setup data under ``key``.
        """
        cls._auto_configurators[key] = fn


class SetupWizard(Wizard):
    finished_template = 'setup/setup_finished.tpl'
    allow_override = True
    start_index = 1
    template_func = template

    def __init__(self, *args, **kwargs):
        super(SetupWizard, self).__init__(*args, **kwargs)
        self._is_completed = False

    @property
    def is_completed(self):
        if not self._is_completed:
            self._is_completed = not self.get_needed_steps()
        return self._is_completed

    def wizard_finished(self, data):
        setup_data = dict()
        for step, step_result in data.items():
            setup_data.update(step_result)

        exts.setup.append(setup_data)
        return template(self.finished_template, setup=exts.setup)

    def exit(self):
        # called to clear the state object which stores the steps that were
        # used while stepping through the wizard, after which clicking back
        # won't work anymore
        self.clear_needed_steps()

    def get_next_setup_step_index(self):
        for step_index, step in sorted(self.steps.items(), key=lambda x: x[0]):
            if step['test']():
                return step_index

        return self.step_count + self.start_index

    def override_next_step(self):
        next_setup_step_index = self.get_next_setup_step_index()
        try:
            wanted_step_index = request.params[self.step_param]
        except KeyError:
            self.set_step_index(next_setup_step_index)
            return
        else:
            try:
                wanted_step_index = int(wanted_step_index)
            except ValueError:
                self.set_step_index(next_setup_step_index)
                return
            else:
                if (wanted_step_index not in self.steps or
                        wanted_step_index > next_setup_step_index):
                    self.set_step_index(next_setup_step_index)
                else:
                    self.set_step_index(wanted_step_index)
