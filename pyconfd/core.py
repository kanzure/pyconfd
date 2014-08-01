"""
Scratchwork. No clue what I want to be doing. Proceed with caution.
"""

import os
import sys
import gevent
import importlib

from pyconfd.plugin import Plugin
from pyconfd.logstuff import log

def import_plugins(path="/etc/pyconfd/conf.d/"):
    """
    Import plugins from the plugin path. Each of the plugin filenames should be
    unique within the namespace of whatever python modules are available (like
    the default standard library, and anything else installed).
    """
    loaded_modules = []

    abspath = os.path.abspath(path)

    # make plugins available for importing
    sys.path.append(abspath)

    # get a list of available plugins
    filenames = os.listdir(abspath)
    log.debug("Found {} files.".format(len(filenames)))

    # Remove ".py" from the name, use filename as module name Assume that all
    # filenames are in the form of "xyz.py".
    module_names = [filename.replace(".py", "") for filename in filenames]

    # import each plugin
    for module_name in module_names:
        log.debug("Importing {}".format(module_name))
        newmodule = importlib.import_module(module_name)
        loaded_modules.append(newmodule)

    return loaded_modules

def find_plugins():
    """
    Finds all subclasses of Plugin. Use this after loading the plugin files.
    """
    log.debug("Searching for loaded plugin subclasses.")
    subclasses = Plugin.__subclasses__()
    subclasses = [subclass for subclass in subclasses if subclass is not Plugin]
    log.debug("Found {} subclasses.".format(len(subclasses)))
    return subclasses

def launch_plugins(plugins):
    """
    Starts looping each plugin. Note that blocking code will block other
    plugins from executing.
    """
    # gevent
    jobs = []

    # plugins is just a list of classes
    for plugin in plugins:
        log.debug("Starting plugin: {}".format(plugin))

        # make an instance of the class
        instance = plugin()

        # async start plugin loop
        newjob = gevent.spawn(instance.loop)
        jobs.append(newjob)

    return jobs

def main():
    """
    Import plugin modules. Find subclasses of Plugin. Use those subclasses.
    """
    modules = import_plugins()
    plugins = find_plugins()
    jobs = launch_plugins(plugins)
    gevent.wait(jobs)

if __name__ == "__main__":
    main()
