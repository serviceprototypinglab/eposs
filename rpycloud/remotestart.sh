host=127.0.0.1 # replace with actual hostname

ssh ubuntu@$host "cd rpycloud && killall python3 && ./start.sh"
