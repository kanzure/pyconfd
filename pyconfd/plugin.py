"""
"""
import os
import subprocess
import shlex

import gevent
import jinja2

from logstuff import log

class PluginException(Exception):
    pass

class Plugin(object):
    """
    Base class for user's config plugins. These plugins will be executed
    through gevent. They check some source of data, then this plugin system
    will generate a config file from a given template, then reload the relevant
    process.
    """

    def __init__(self):
        """
        Construct a new plugin.
        """
        # where is the jinja template?
        if not hasattr(self, "src"):
            raise PluginException("There must be a 'src' jinja template path.")

        # should be a template destination
        if not hasattr(self, "dest"):
            raise PluginException("There must be a 'dest' value.")

        # check_cmd can be skipped (checks config validity)
        if not hasattr(self, "check_cmd"):
            self.check_cmd = None

        # reload_cmd can be skipped (maybe the config file is watched separately?)
        if not hasattr(self, "reload_cmd"):
            self.reload_cmd = None

        # keeps track of the last set of config values
        self._last_config = None

    def sleep(self):
        """
        Sleep before checking again. The better way to do this would be to
        implement in consul some concept of event-based notification hooks that
        would call a script. And then pyconfd wouldn't have to be a daemon.
        """
        seconds = 5

        log.debug("Sleeping for {} seconds".format(seconds))

        # seconds to sleep (fractional values are okay)
        gevent.sleep(seconds)

        log.debug("Done sleeping for {} seconds.".format(seconds))

    def get(self):
        """
        Grab possibly new configuration from some external source. Both consul
        or etcd could work here. Return a dictionary.
        """
        raise NotImplementedError("Subclass must implement its own get method.")

    def generate(self, template_input, template_path="/etc/pyconfd/templates/"):
        """
        Populate the template from the given input.
        """
        log.debug("Reading the template.")

        srcpath = os.path.join(template_path, self.src)

        # load template content
        with open(srcpath, "r") as template_fh:
            template_content = template_fh.read()

        # populate the template
        log.debug("Populating the template.")
        template = jinja2.Template(template_content)
        populated = template.render(**template_input)

        return populated

    def loop(self):
        """
        Executes this plugin. Waits an interval amount of time before checking
        the config. Updates config files when necessary. Restarts programs.
        """
        executing = True
        while executing:
            try:
                # determines if config is new
                skip = False

                # grab config data via custom method
                log.debug("Getting the data.")
                data = self.get()
            except Exception as exc:
                log.error("Error getting data: {}".format(exc))
            else: # didn't fail
                # somehow i doubt jinja responds well to None
                if data is None:
                    data = {}

                # never skip the first time (it's None)
                if self._last_config is not None:
                    # skip when new config same as old config
                    if self._last_config == data:
                        skip = True

                if not skip:
                    try:
                        # populate the template
                        populated = self.generate(data)
                    except Exception as exc:
                        # TODO: log error, don't bail
                        log.error("Failed to populate the template: {}".format(exc))
                    else:
                        self.write_config(populated)
                        self.reload_process()
                else:
                    log.debug("No new data. Skipping.")
            finally:
                # only set latest config if it was actually used
                if not skip:
                    self._last_config = data

                # wait predefined time
                self.sleep()

    def write_config(self, config):
        """
        Write the config file with the given content.
        """
        log.debug("Writing config to {}".format(self.dest))
        with open(self.dest, "w") as config_fh:
            config_fh.write(config)

    def reload_process(self):
        """
        Execute the reload_cmd command.

        Sometimes a daemon might watch its own config file for changes and
        reload on its own, so reload_cmd is not mandatory.

        Users of supervisord can use a "reload_cmd" value of:
            supervisordctl reload haproxy
        .. but the default is to kill haproxy and start a new process (killing
        all of the existing connections), so be warned about that.

        Also of note to supervisord users::

            Unfortunately supervisor doesn't offer a way to provide a custom
            restart command, so doing an uninterrupted haproxy restart via
            supervisor isn't possible. Instead make sure you have autorestart
            set to unexpected (the default) rather than true (which is what I
            usually do) - that way if you want a clean haproxy restart you can
            just do it yourself at the commandline using the -sf option as
            normal.

        from http://mark.aufflick.com/blog/2012/03/25/supervisord-supervisorctl-cheat-sheet
        """
        # maybe it watches its own config and reloads voluntarily
        if self.reload_cmd is not None and self.reload_cmd is not "":
            log.debug("Running reload_cmd: {}".format(self.reload_cmd))
            args = shlex.split(self.reload_cmd)
            process = subprocess.Popen(args)
            log.debug("Okay, done launching reload_cmd.")
