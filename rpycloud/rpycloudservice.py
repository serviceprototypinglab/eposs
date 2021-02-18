import flask
import os
import random
import rpyc
import time
import glob
import sys

auth_cred = True
auth_user = False

def runweb(network):
    sessions = {}
    creds = {}
    app = flask.Flask(__name__)

    def log(host, func, p):
        t = time.time()
        f = open(f"{host}.log", "a")
        print(f"{t},{flask.request.remote_addr},{func},{str(p)}", file=f)
        f.close()

    @app.route("/", methods=["GET"])
    def index():
        return "RPyCloud Service. You are using it the wrong way."

    @app.route("/dashboard", methods=["GET"])
    def dash():
        rows = []
        evs = glob.glob("ev3-*.log")
        for ev in evs:
            f = open(ev)
            lines = f.readlines()
            f.close()
            stamp = int(float(lines[-1].split(",")[0]))
            diff = round(time.time() - stamp)
            if diff < 120:
                last = f"{diff}s ago"
            else:
                last = f"{int(diff / 60)}min ago"
            evbot = ev.split(".")[0]
            sess = len([line for line in lines if line.split(",")[2] == "boot"])
            row = f"<tr><td>{evbot}</td><td>{sess}</td><td>{len(lines)}</td><td>{last}</td></tr>"
            rows.append(row)
        rows = "".join(rows)
        return f"""
            <html>
            <head>
            <title>RPyCloud Service Dashboard</title>
            </head>
            <body>
            <h1>RPyCloud Service Dashboard</h2>
            <table border=1>
            <tr><th>Robot</th><th>Sessions</th><th>Activities</th><th>Last active</th></tr>
            {rows}
            </table>
            </body>
            </html>
        """

    @app.route("/<func>/<p>/<key>", methods=["POST"])
    def cloudcall(func, p, key):
        key = int(key)
        if key in sessions:
            ev = sessions[key]
            #px = ",".join(p)
            if "os." in p:
                print("// unsafe eval", p)
                return ""
            p, np = eval(p)
            px = str(p)
            for k, v in np.items():
                px = px[:-1] + ", " + str(k) + "=" + repr(v) + px[-1]
            code = f"ev.{func}{px}"
            print("// session ->", ev, "code ->", code)
            n = eval(code)
            return str(n)
        return ""

    @app.route("/boot/<host>/<cred>", methods=["POST"])
    def boot(host, cred):
        print("// boot", host, cred)
        creds[host] = cred
        log(host, "boot", None)
        return "OK"

    @app.route("/connect/<host>/<port>/<cred>", methods=["POST"])
    def connectregister(host, port, cred):
        if auth_cred:
            if not host in creds or creds[host] != cred:
                print("// auth error", host, port, cred)
                return "0"
        else:
            print("// skipping auth")

        hostfqdn = host
        if not "." in host:
            if network:
                hostfqdn = host + "." + network

        magnitude = 1000000
        k = random.randrange(magnitude, 10 * magnitude)
        try:
            session = rpyc.connect(hostfqdn, port=port).root
        except:
            print("// connect error", host, port)
            session = None
        else:
            log(host, "connect", None)
        if session:
            sessions[k] = session
        else:
            k = 0
        return str(k)

    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)), ssl_context=None)

if __name__ == "__main__":
    network = None
    if len(sys.argv) == 2:
        network = sys.argv[1]
    runweb(network)
