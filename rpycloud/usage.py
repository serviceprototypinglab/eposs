import rpycloudmin as rpyc
ev3 = rpyc.connect("ev3-NAME", port=8401, cred=666, cloud="127.0.0.1:10080").root
ev3.speak("We are the robots")
