pyconfd is like [confd](https://github.com/kelseyhightower/confd) but written
in python. Instead of plaintext configuration files, use python to write a tiny
bit of code to query anything, which is then used to render a jinja2 template.

# installation

``` bash
pip install pyconfd
```

# setup

``` bash
# store python plugins here
mkdir -p /etc/pyconfd/conf.d/

# store jinja templates here
mkdir -p /etc/pyconfd/templates/
```

Also, make sure that pyconfd is launched.

# usage

Launch pyconfd directly:

``` bash
pyconfd
```

At the moment, there is no daemon mode. Users of supervisord can write a supervisor config file like:

```
[program:pyconfd]
command=pyconfd
numprocs=1
numprocs_start=0
priority=30
autostart=true
autorestart=unexpected
startsecs=30
startretries=10
exitcodes=0,2
stopsignal=TERM
stopwaitsecs=10
directory=/
user=root
redirect_stderr=false
stdout_logfile=/data/log/supervisor/pyconfd.out
stdout_logfile_maxbytes=1MB
stdout_logfile_backups=10
stderr_logfile=/data/log/supervisor/pyconfd.err
stderr_logfile_maxbytes=1MB
stderr_logfile_backups=10
```

# plugin example

Check out the [examples](https://github.com/kanzure/pyconfd/tree/master/examples). Basically put this in in a .py file in /etc/pyconfd/conf.d/ and write something like:

``` python
import pyconfd
import random

class BashPlugin(pyconfd.Plugin):
    # filename of template from /etc/pyconf.d/templates/
    src = "bash.cfg.tmpl"

    # where to dump the generated config file
    dest = "/tmp/bash.cfg"

    # force reload of daemon, consider using supervisordctl
    reload_cmd = "bash -c 'exit'"

    def get(self):
        return {"number": random.randrange(1, 101)}
```

And the jinja template bash.cfg.tmpl can look like:

```
echo "The number is: {{ number }}"
```

# real-world plugins

The plugin's "get" method can be written to do whatever. I often use it with [consul](https://consul.io/) like with [consulate](https://pypi.python.org/pypi/consulate) or [pyconsul](https://pypi.python.org/pypi/pyconsul). Others may prefer to query [etcd](https://github.com/coreos/etcd).

## consulate

Extract a list of servers running a certain service, and their IP addresses.

``` python
import pyconfd
import consulate

class HAProxy(pyconfd.plugin):
    def get(self):
        """
        Get relevant variables from consul.

        :rtype: dict
        """
        data = {"servers": {}}
        session = consulate.Consulate()
        services = session.catalog.services().keys()
        for service in services:
            data["servers"][service] = []
            servers = session.catalog.service(service)
            for server in servers:
                ip_address = server["Address"]
                data["servers"][service].append(ip_address)
        return data
```

# future work

* daemon mode
* tests
* Switch away from gevent.sleep and use consul hooks to trigger config updates. This will deprecate most of this library.

# license

BSD
