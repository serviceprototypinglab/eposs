# Manually register a robot PIN and then perform sample movement

#ROBOT=192.168.178.30
ROBOT=ev3-NAME

PIN=162

curl -X POST http://localhost:8080/boot/$ROBOT/$PIN

python3 rpycloud.py $ROBOT
