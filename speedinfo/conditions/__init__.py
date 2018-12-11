# coding: utf-8

from importlib import import_module

from speedinfo.settings import speedinfo_settings


class ConditionsDispatcher:
    def __init__(self):
        self.conditions = None

    def import_conditions(self):
        self.conditions = []

        for module_path in speedinfo_settings.SPEEDINFO_PROFILING_CONDITIONS:
            path, class_name = module_path.rsplit('.', 1)

            try:
                module = import_module(path)
                self.conditions.append(
                    getattr(module, class_name)()
                )
            except (AttributeError, ImportError) as e:
                msg = 'Could not import "{}". {}: {}.'.format(module_path, e.__class__.__name__, e)
                raise ImportError(msg)

    def get_conditions(self):
        if self.conditions is None:
            self.import_conditions()

        return self.conditions


conditions_dispatcher = ConditionsDispatcher()
