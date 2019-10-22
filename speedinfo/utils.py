# coding: utf-8

from importlib import import_module


def import_class(module_path):
    """Import class by string path.

    :param str module_path: Path to class to import (e.g. 'speedinfo.profiler.Profiler')
    :raises ImportError: if path to class is invalid
    :return: imported class
    """
    path, class_name = module_path.rsplit(".", 1)

    try:
        module = import_module(path)
        return getattr(module, class_name)
    except (AttributeError, ImportError) as e:
        msg = "Could not import '{}'. {}: {}.".format(module_path, e.__class__.__name__, e)
        raise ImportError(msg)
