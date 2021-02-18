import rpyc
import sys

if len(sys.argv) < 2:
    print("Synopsis: emergencystop <car> [<basespeed>]", file=sys.stderr)
    exit(1)
car = sys.argv[1]

ev3 = rpyc.connect(car, port=8401).root

spd = 40
if len(sys.argv) >= 3:
    spd = int(sys.argv[2])

ev3.left(spd)
ev3.right(spd)

lim = spd * 0.75

toggle = 0

ev3.led("LEFT", "GREEN")
ev3.led("RIGHT", "GREEN")
ev3.speak("autonomous driving activated")

ev3.on()
while True:
    dst = ev3.sonic()
    print("#", dst, "limit", lim)
    ev3.led("LEFT", "BLACK")
    ev3.led("RIGHT", "BLACK")
    if dst < lim or abs(dst - 255) < 0.1:
        ev3.stop()
        break

    if toggle == 0:
        ev3.led("LEFT", "AMBER")
    else:
        ev3.led("RIGHT", "AMBER")
    toggle = 1 - toggle

for i in range(3):
    ev3.led("LEFT", "RED")
    ev3.led("RIGHT", "RED")
    ev3.led("LEFT", "BLACK")
    ev3.led("RIGHT", "BLACK")

ev3.speak("emergency stop completed")
