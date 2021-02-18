import flask
import os
import time
import pika
import json
import base64
import io
import sys
try:
    import flask_cors
    print("CORS active.")
except:
    print("! No CORS support.")

broker = "localhost"

secure_deviceboot = True

def runwebproxy(broker):
    app = flask.Flask(__name__)
    if "flask_cors" in globals():
        cors = flask_cors.CORS(app)
        app.config["CORS_HEADERS"] = "Content-Type"

    if broker != "none":
        connection = pika.BlockingConnection(pika.ConnectionParameters(broker, heartbeat=0))
        channel = connection.channel()
        channel.queue_declare(queue="rpycloud")
        bchannel = connection.channel()
        bchannel.queue_declare(queue="rpycloud-response")
        cchannel = connection.channel()
        cchannel.queue_declare(queue="rpycloud-cam")
    else:
        channel = None
        bchannel = None
        cchannel = None

    def log(line):
        t = time.time()
        logline = f"{t},{flask.request.remote_addr},{line}"
        f = open("proxy.log", "a")
        print(logline, file=f)
        f.close()
        print("#LOG", logline)

    def publish(msg, bchannel):
        if not bchannel:
            return "SIMULATION-WITHOUT-BROKER"

        channel.basic_publish(exchange="", routing_key="rpycloud", body=json.dumps(msg))

        while True:
            try:
                for method_frame, properties, body in channel.consume("rpycloud-response"):
                    msg = body.decode()
                    channel.basic_ack(method_frame.delivery_tag)
                    print("#RESPONSE", msg)
                    return msg
            except Exception as e:
                print("- queue presumably not yet ready; wait 1s /", e)
                time.sleep(1)
                continue

    @app.route("/", methods=["GET"])
    def index():
        return "RPyCloud Proxy. You are using it the wrong way (twice even)."

    @app.route("/<func>/<p>/<key>", methods=["POST"])
    def cloudcall(func, p, key):
        log(f"/{func}/{p}/{key}")
        return publish((func, p, key), bchannel)

    @app.route("/boot/<host>/<cred>", methods=["POST"])
    def boot(host, cred):
        # Security: No forwarding of device booting
        if not secure_deviceboot:
            log(f"/boot/{host}/{cred}")
            return publish(("boot", host, cred), bchannel)
        else:
            print("#FOILED device boot", host, cred)

    @app.route("/connect/<host>/<port>/<cred>", methods=["POST"])
    #@flask_cors.cross_origin()
    def connectregister(host, port, cred):
        log(f"/connect/{host}/{port}/{cred}")
        return publish(("connect", host, port, cred), bchannel)

    @app.route("/cam", methods=["GET"])
    def camera():
        print("-- check cam")
        if not cchannel:
            return

        try:
            method_frame, properties, body = cchannel.basic_get("rpycloud-cam")
            print("CAM OK", len(body))
            msgbin = base64.b85decode(body)
            cchannel.basic_ack(method_frame.delivery_tag)
            return flask.send_file(io.BytesIO(msgbin), mimetype="image/jpeg")
        except Exception as e:
            print("CAM empty")
            return ""

    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8081)), ssl_context=None)

if __name__ == "__main__":
    if len(sys.argv) == 2:
        broker = sys.argv[1]
    print("Using broker:", broker)

    runwebproxy(broker)
