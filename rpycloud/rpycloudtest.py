import rpycloud as rpyc
import time

robot = "ev3-NAME"
pin = 666

evx = rpyc.connect(robot, port=8401, cred=pin, cloud="127.0.0.1:8081").root
evx.speak("test drive")
evx.left(25)
evx.right(25)
evx.on()
evx.led("LEFT", "AMBER")
evx.led("RIGHT", "AMBER")
time.sleep(3)
evx.stop()
evx.led("LEFT", "BLACK")
evx.led("RIGHT", "BLACK")
