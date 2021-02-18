import rpyc
import sys
import time

if len(sys.argv) < 2:
    print("Synopsis: backforth <car>", file=sys.stderr)
    exit(1)
car = sys.argv[1]

ev3 = rpyc.connect(car, port=8401).root

x = 12
p = 1

for i in range(5):
    ev3.left(10)
    ev3.right(10)
    ev3.on()
    time.sleep(x)
    ev3.stop()
    time.sleep(p)
    ev3.left(-10)
    ev3.right(-10)
    ev3.on()
    time.sleep(x)
    ev3.stop()
    time.sleep(p)
