__author__ = 'zephyryin'
from baseClass import *

rangeRover = Car()
while 1:

    print '     start with 1 sensor :   1'
    print '     start with 2 sensor :   2'
    print '     draw map            :   3'
    print '     quit                :   4'
    print 'please input cmd:'
    cmd = raw_input()
    if cmd == '1':
        rangeRover.followBlackWithOneSensor()
    elif cmd == '2':
        rangeRover.followBlackWithTwoSensors()
    elif cmd == '3':
        if len(rangeRover.turnLog) == 0:
            rangeRover.readTurnFromLog()
        rangeRover.drawMap()
    elif cmd == '4':
        break
    else:
        print 'error command'
        continue

