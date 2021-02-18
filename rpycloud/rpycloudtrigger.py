import os
import pika
import json
import time
import urllib.request
import urllib.parse
import sys

broker = "localhost"
backend = "127.0.0.1:8080"

def forward(msg, bchannel):
    if msg[0] == "boot":
        path = "/boot/" + "/".join(msg[1:])
    elif msg[0] == "connect":
        path = "/connect/" + "/".join(msg[1:])
    else:
        msg[-2] = urllib.parse.quote(bytes(str(msg[-2]), "utf-8"))
        path = "/" + "/".join(msg)

    fullpath = "http://" + backend + path
    print("!!!", fullpath)

    req = urllib.request.Request(fullpath, method="POST")
    f = urllib.request.urlopen(req)
    resp = f.read().decode()

    print("->->->", resp)
    bchannel.basic_publish(exchange="", routing_key="rpycloud-response", body=resp)

def runproxyclient(broker):
    connection = pika.BlockingConnection(pika.ConnectionParameters(broker, heartbeat=0))
    channel = connection.channel()
    channel.queue_declare(queue="rpycloud")
    bchannel = connection.channel()
    bchannel.queue_declare(queue="rpycloud-response")

    while True:
        try:
            for method_frame, properties, body in channel.consume("rpycloud"):
                msg = json.loads(body.decode())
                channel.basic_ack(method_frame.delivery_tag)
                forward(msg, bchannel)
        except Exception as e:
            print("- queue presumably not yet ready; wait 1s /", e)
            time.sleep(1)
            continue

if __name__ == "__main__":
    if len(sys.argv) == 2:
        broker = sys.argv[1]

    runproxyclient(broker)
