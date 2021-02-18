import os
import pika
import time
import base64

broker = "localhost"
PERIOD = 2

def runcam():
    connection = pika.BlockingConnection(pika.ConnectionParameters(broker, heartbeat=0))
    channel = connection.channel()
    channel.queue_declare(queue="rpycloud-cam")

    while True:
        stime = time.time()
        fname = "/tmp/cam-tmp.jpg"
        print(f"Recording to {fname}...")
        os.system(f"fswebcam -d /dev/video0 -r 640x480 --jpeg 85 -F 1 {fname}")
        f = open(fname, "rb")
        binpic = f.read()
        f.close()
        b85pic = base64.b85encode(binpic)
        print(f"Submitting recording.")
        channel.basic_publish(exchange="", routing_key="rpycloud-cam", body=b85pic)
        etime = time.time()
        diff = round(etime - stime, 2)
        rem = PERIOD - diff
        print("Needed", diff, "s; sleep remainder of", rem, "s")
        time.sleep(rem)

if __name__ == "__main__":
    runcam()
