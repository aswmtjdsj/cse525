__author__ = 'zephyryin'
import nxt
import sys
import time
from nxt.sensor import *
from nxt.sensor.hitechnic import *

class Car:
    def __init__(self):
        self.brick = nxt.find_one_brick()
        self.motors = [nxt.Motor(self.brick, nxt.PORT_A), nxt.Motor(self.brick, nxt.PORT_B)]
        #self.colorSensors = [Colorv2(self.brick, PORT_1)]
        self.colorSensors = [Colorv2(self.brick, PORT_1), Colorv2(self.brick, PORT_4)]
        self.previousColor = ''
        self.decisionLog = []           # record each move
        self.turnLog = []               # record each corner
        self.minimumPower = 64
        self.stepTime = 0.1

    def getCurrentColor(self):
        colors = []
        for colorSensor in self.colorSensors:

            value = colorSensor.get_sample()

            # print 'number: ', value.number,
            # print ', red: ', value.red,
            # print ', green: ', value.green,
            # print ', blue: ', value.blue,
            # print ', white: ', value.white,
            # print ', index: ', value.index,
            # print ', |red|: ', value.normred,
            # print ', |green|: ', value.normgreen,
            # print ', |blue|: ', value.normblue

            if value.white > 200 and value.normred > 200 and value.normgreen > 200 and value.normblue > 200:
                colors.append('white')
            elif value.normred == 255 and value.normgreen < 100 and value.normblue < 100:
                colors.append('red')
            elif value.red < 50 and value.green < 50 and value.blue < 50:
                colors.append('black')
            else:
                colors.append('black')
        return colors

    def move(self, power = 70, direction = 1):       # move forward or backward
        scale = (1 if direction == 1 else -1)
        self.motors[0].run(scale * power)
        self.motors[1].run(scale * power)

    def followBlackWithOneSensor(self):
        while 1:
            colors = self.getCurrentColor()
            currentColor = colors[0]
            print currentColor
            if currentColor == 'black':
                self.stepRight()
            elif currentColor == 'white':
                self.stepLeft()
            elif currentColor == 'red':
                print 'destination reached'
                return
            time.sleep(0.1)

    def followBlackWithTwoSensors(self):

        decisionFile = open('decisionLog.txt','w')
        mapFile = open('turnLog.txt', 'w')
        startTime = time.clock()
        while 1:
            colors = self.getCurrentColor()
            leftColor = colors[0]
            rightColor = colors[1]
            print leftColor + ' : ' + rightColor
            if leftColor == 'red' or rightColor == 'red':
                self.stop()
                self.decisionLog.append('end')
                print 'goal reached'
                return
            elif leftColor == 'white' and rightColor == 'white':
                #self.moveOneStep()
                self.move(63)
                self.decisionLog.append('move')
            elif leftColor == 'black' and rightColor == 'white':
                self.stop()
                if len(self.decisionLog) >= 2 and self.decisionLog[-1] == 'right' and self.decisionLog[-2] == 'right':      # make a huge turn at the conner
                    self.turnRight()
                    self.decisionLog.append('turnRight')
                    elapsed = time.clock() - startTime
                    startTime = time.clock()
                    mapFile.write('turnRight:' + str(elapsed) + '\n')
                else:
                    self.stepRight()
                    self.decisionLog.append('right')
            elif leftColor == 'white' and rightColor == 'black':
                self.stop()
                if len(self.decisionLog) >= 2 and self.decisionLog[-1] == 'left' and self.decisionLog[-2] == 'left':        # make a huge turn at the conner
                    self.turnLeft()
                    self.decisionLog.append('turnLeft')
                    elapsed = time.clock() - startTime
                    startTime = time.clock()
                    mapFile.write('turnLeft:' + str(elapsed) + '\n')
                else:
                    self.stepLeft()
                    self.decisionLog.append('left')
            elif leftColor == 'black' and rightColor == 'black':
                self.stop()
                self.moveOneStep()
            else:
                self.stop()
                print 'condition unhandled'
                break
            decisionFile.write(str(self.decisionLog[-1] + '\n'))
            #time.sleep(0.1)                 # hold for a moment after each move
        decisionFile.close()
        mapFile.close()


    def stepRight(self, direction = 1, power = 70, runTime = 0.1):
        scale = (1 if direction == 1 else -1)
        mRight = self.motors[1]
        mRight.run(power * scale)
        time.sleep(runTime)
        mRight.brake()


    def stepLeft(self, direction = 1, power = 70, runTime = 0.1):
        scale = (1 if direction == 1 else -1)
        mleft = self.motors[0]
        mleft.run(power * scale)
        time.sleep(runTime)
        mleft.brake()

    def moveOneStep(self, direction = 1, power = 70,  runTime = 0.1):       # move forward or backward
        scale = (1 if direction == 1 else -1)
        self.motors[0].run(scale * power)
        self.motors[1].run(scale * power)
        time.sleep(runTime)
        self.motors[0].brake()
        self.motors[1].brake()


    def stop(self):
        for motor in self.motors:
            motor.brake()

    def turnRight(self, degrees = 250):
        self.stepLeft(-1)
        rightMotor = self.motors[1]
        rightMotor.turn(self.minimumPower, degrees)

    def turnLeft(self, degrees = 250):
        self.stepRight(-1)
        leftMotor = self.motors[0]
        leftMotor.turn(self.minimumPower, degrees)


    def drawMap(self):
        pass

    def createPath(self):
        path = []
        for i in range(len(self.decisionLog)):
            if len(path) == 0 or self.decisionLog[i] == 'move':
                path.append(self.decisionLog[i])
                continue
            if self.decisionLog[i] == 'left':
                if path[-1] == 'right':
                    path.pop()
                    path.append('move')
                elif path[-1] == 'left':
                    pass

    def consistence(self):
        while 1:
            colors = self.getCurrentColor()
            leftColor = colors[0]
            rightColor = colors[1]
            if leftColor == 'white' and rightColor == 'white':
                self.move()
            elif leftColor == 'black' and rightColor == 'white':
                self.stop()
                self.stepRight()
                self.move()
            elif leftColor == 'white' and rightColor == 'black':
                self.stop()
                self.stepLeft()
                self.move()
    #
    # def adjustDirection(self, power = 60):
    #     found = False
    #     mLeft = self.motors[0]
    #     mRight = self.motors[1]
    #     degree = 20
    #     while degree < 360:
    #         mLeft.turn(power, degree)           # try left
    #         time.sleep(0.5)
    #         if self.getCurrentColor() == 'black':
    #             self.previousColor = 'black'
    #             return
    #         mLeft.turn(-power, degree)          # go back
    #
    #         mRight.turn(power, degree)          # try right
    #         time.sleep(0.5)
    #         if self.getCurrentColor() == 'black':
    #             self.previousColor = 'black'
    #             return
    #         mRight.turn(-power, degree)         # go back
    #         degree += 20
    #
    # def followBlackwithOneSensor(self):
    #     finished = False
    #     while not finished:
    #         currentColor = self.getCurrentColor()
    #         if currentColor == 'black' and self.previousColor == 'black' or self.previousColor == '':
    #             self.move()
    #         else:
    #             self.stop()
    #             self.adjustDirection()
    #             continue
    #         self.previousColor = currentColor





