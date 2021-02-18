# Run the queue listener and local service triggered by queue events
# (an extension to rpycloudauth.sh)

proxy=127.0.0.1

#ROBOT=192.168.178.30
ROBOT=ev3-NAME

PIN=162

xterm -e "python3 rpycloudtrigger.py $proxy" &
xterm -e "python3 rpycloudservice.py" &

echo "Wait for local auth..."
sleep 3

curl -X POST http://127.0.0.1:8080/boot/$ROBOT/$PIN
