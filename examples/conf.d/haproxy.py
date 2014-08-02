"""
pyconfd example template plugin. This file is loaded by pyconfd. The get
function is called by pyconfd and returns the current dictionary of values to
populate the template with. If the values are different, the template generator
is executed and the target service reloads.

this goes here: /etc/pyconfd/conf.d/haproxy.py
"""

import gevent

# only required because of the pointless Plugin.generate override
import jinja2

import pyconfd

class HAProxyPlugin(pyconfd.Plugin):

    # config template is from /etc/pyconfd/templates/
    src = "haproxy.cfg.tmpl"

    # where to dump the generated config
    dest = "/etc/haproxy/haproxy.cfg"

    # check generated config file (not mandatory)
    #check_cmd = "/usr/sbin/haproxy -c -q -f {{ dest }}"

    # Safely reload the process. Also, if you are using supervisord you can run
    # "supervisordctl reload haproxy", but it would drop active connections.
    reload_cmd = "/usr/sbin/haproxy -f {{ dest }} -p /var/run/haproxy.pid -sf $(</var/run/haproxy.pid)"

    def get(self):
        """
        Get relevant variables from consul.

        :rtype: dict
        """
        # dict will be used by Plugin.generate if it has a different value
        return {}

    # totally unnecessary (handled in parent class)
    def generate(self, template_input):
        with open(self.src, "r") as template_fh:
            template = jinja2.Template(template_fh.read())
        return template.render(**template_input)

    # also unnecessary
    def sleep(self):
        """
        Sleep before checking again. In the future, there may be an event-based
        method of triggering config updates, where pyconfd could be replaced
        entirely by separate scripts hooked up as consul notifiers.
        """
        # number of seconds to sleep (fractional values are okay)
        gevent.sleep(5)
