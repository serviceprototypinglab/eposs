# Integrate into buggy.py before start of ThreadedServer with: 
#    import rpyclouddevice
#    rpyclouddevice.rpycloudboot()
# Make sure to adjust the cloud endpoint address

def speak(s, offdevice):
    if offdevice:
        print("SPEAK: " + s)
    else:
        from ev3dev2.sound import Sound
        Sound().speak(s)

def rpycloudbootname(name, offdevice=False):
    import random
    import urllib.request
    cred = random.randrange(100, 1000)
    speak("Cloud robotics edition.", offdevice=offdevice)
    res = "http://X.X.X.X:8080/boot/" + name + "/" + str(cred)
    req = urllib.request.Request(res, method="POST")
    try:
        f = urllib.request.urlopen(req)
    except Exception as e:
        speak("Connection to cloud failed.", offdevice=offdevice)
        f = open("error.log", "a")
        print("EXCEPTION", e, file=f)
        f.close()
    else:
        speak("Connection credential " + str(cred), offdevice=offdevice)

def rpycloudboot(offdevice=False):
    import os
    rpycloudbootname(os.uname()[1], offdevice=offdevice)

if __name__ == "__main__":
    #rpycloudbootname("ev3-NAME", offdevice=True)
    rpycloudboot(offdevice=True)
