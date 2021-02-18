# RPyCloud: Drop-in replacement for 'rpyc' that redirects all EV3 control through the cloud.
# See rpycloud.pdf for documentation.

import sys
import time
import math
import functools
import urllib.request
import urllib.parse

epdefault = "http://127.0.0.1:8080"

class EV3Cloud:
    def __init__(self, host, port, cred=None, cloud=None, user=None, password=None):
        if cloud:
            if not ":" in cloud:
                cloud = cloud + ":8080"
            if not "http" in cloud:
                cloud = "http://" + cloud

        self.root = None
        self.host = host
        self.port = port
        self.cred = cred
        self.cloud = cloud
        self.user = user
        self.password = password
        self.key = None

    def connect(self):
        if self.cloud:
            ep = self.cloud
        else:
            ep = epdefault
        res = f"{ep}/connect/{self.host}/{self.port}/{self.cred}"
        req = urllib.request.Request(res, method="POST")
        f = urllib.request.urlopen(req)
        key = f.read().decode()
        self.key = key
        print("// connect", key)

class EV3ManagedRoot:
    def __init__(self, ev3base, ev3, key=None):
        self.ev3base = ev3base
        self.ev3 = ev3
        self.key = key

    def __getattr__(self, a):
        print("// root", a)
        return functools.partial(self.cloudcall, a)

    def cloudcall(self, func, *p, **np):
        print("// cloud", func, p, np)

        if self.ev3base.cloud:
            ep = self.ev3base.cloud
        else:
            ep = epdefault

        pp = urllib.parse.quote(bytes(str((p, np)), "utf-8"))
        res = f"{ep}/{func}/{pp}/{self.key}"
        print("// -> cloud", res)

        req = urllib.request.Request(res, method="POST")
        f = urllib.request.urlopen(req)
        r = f.read().decode()
        print("// -> cloud result", r)

class EV3Managed:
    def __init__(self, ev3base):
        self.ev3base = ev3base
        self.ev3base.connect()
        self.ev3root = EV3ManagedRoot(ev3base, ev3base.root, ev3base.key)

    def __getattr__(self, a):
        if a == "root":
            return self.ev3root
        print("// unsupported attribute in base", a)
        #return eval(f"self.ev3base.{a}")

def connect(host, port, cred=None, cloud=None, user=None, password=None):
    return EV3Managed(EV3Cloud(host, port, cred, cloud, user, password))

if __name__ == "__main__":
    #evx = connect("ev3-NAME", port=8401, cred=0, cloud="127.0.0.1", user="x", password="y").root
    # Optional attributes: "cloud" (e.g. "127.0.0.1", "user"/"password" (not yet used))
    robot = sys.argv[1]
    evx = connect(robot, port=8401, cred=0).root # TODO: enter the number spoken by the robot after boot here
    evx.left(25)
    evx.right(15)
    evx.on()
    time.sleep(3)
    evx.stop()
