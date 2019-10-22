# coding: utf-8

from speedinfo.conf import speedinfo_settings
from speedinfo.utils import import_class


class ConditionsDispatcher:
    def __init__(self):
        self.conditions = None

    def import_conditions(self):
        self.conditions = []

        for module_path in speedinfo_settings.SPEEDINFO_PROFILING_CONDITIONS:
            self.conditions.append(import_class(module_path)())

    def get_conditions(self):
        if self.conditions is None:
            self.import_conditions()

        return self.conditions


conditions_dispatcher = ConditionsDispatcher()
