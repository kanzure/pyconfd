import pyconfd
import random

class BashPlugin(pyconfd.Plugin):
    src = "bash.cfg.tmpl"
    dest = "/tmp/bash.cfg"
    reload_cmd = "bash -c 'exit'"

    def get(self):
        return {"number": random.randrange(1, 101)}
