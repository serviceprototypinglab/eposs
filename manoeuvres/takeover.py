import rpyc
import sys
import time

BEHAVIOUR_EMERGENCYSTOP = 1
BEHAVIOUR_TAKEOVER = 2
BEHAVIOUR_ADJUST = 3

if len(sys.argv) < 2:
    print("Synopsis: takeover <car> [<basespeed>] [behaviour]", file=sys.stderr)
    exit(1)
car = sys.argv[1]

ev3 = rpyc.connect(car, port=8401).root

spd = 10
if len(sys.argv) >= 3:
    spd = int(sys.argv[2])

behaviour = BEHAVIOUR_EMERGENCYSTOP
if len(sys.argv) >= 4 and sys.argv[3] == "takeover":
    behaviour = BEHAVIOUR_TAKEOVER

ev3.left(spd)
ev3.right(spd)

lim = spd * 0.75
if behaviour == BEHAVIOUR_TAKEOVER:
    lim = spd * 2.2
    ev3.led("LEFT", "AMBER")
    ev3.led("RIGHT", "AMBER")

ev3.on()
overcounter = 0
adjust = 1.0
lasttime = None
while True:
    dst = ev3.sonic()
    print("#", dst, "limit", lim)
    if dst < lim or abs(dst - 255) < 0.1:
        if behaviour == BEHAVIOUR_EMERGENCYSTOP:
            ev3.stop()
            ev3.speak("emergency stop completed")
            break
        elif behaviour == BEHAVIOUR_TAKEOVER and not overcounter:
            print("--RIGHT")
            ev3.stop()
            ev3.speak("take over now")
            #time.sleep(5)
            ev3.left(spd)
            ev3.right(spd * 3)
            ev3.on()
            overcounter = 1
            lasttime = time.time()
    if overcounter:
        #overcounter += 1
        if overcounter == 1 and time.time() > lasttime + 1.8:
            print("--LEFT")
            ev3.stop()
            #ev3.speak("left")
            #time.sleep(5)
            ev3.left(spd * 3)
            ev3.right(spd)
            ev3.on()
            overcounter += 1
            lasttime = time.time()
        if overcounter == 2 and time.time() > lasttime + 1.8 - adjust:
            print("--GO")
            ev3.stop()
            #ev3.speak("go")
            #time.sleep(5)
            ev3.left(spd * 3)
            ev3.right(spd * 3)
            ev3.on()
            ev3.speak("go fast")
            behaviour = BEHAVIOUR_EMERGENCYSTOP
            overcounter = 0
            lasttime = None
        #elif overcounter == 10:

ev3.led("LEFT", "BLACK")
ev3.led("RIGHT", "BLACK")
