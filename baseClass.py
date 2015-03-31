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
        self.colorLog = [('white','white')]
        self.decisionLog = []           # record each move
        self.turnLog = []               # record each corner
        self.runPower = 70
        self.turnPower = 70
        self.bigTurnDegree = 70         # 70
        self.stepTime = 0.1
        self.minimumElapse = 0.2
        self.penAxis = 'leftMotor'
        self.turnLogFileName = 'turnLog.txt'
        self.decisionLogFileName = 'decisionLog.txt'

    def getCurrentColor(self, degbug = False):
        colors = []
        for colorSensor in self.colorSensors:

            value = colorSensor.get_sample()
            if degbug:
                print 'number: ', value.number,
                print ', red: ', value.red,
                print ', green: ', value.green,
                print ', blue: ', value.blue,
                print ', white: ', value.white,
                print ', index: ', value.index,
                print ', |red|: ', value.normred,
                print ', |green|: ', value.normgreen,
                print ', |blue|: ', value.normblue

            whiteThreshold = 200
            blackthreshold = 50

            if value.white > whiteThreshold and value.red > whiteThreshold and value.green > whiteThreshold and value.blue > whiteThreshold:
                colors.append('white')
            elif value.normred == 255 and value.normgreen < 100 and value.normblue < 100:
                colors.append('red')
            elif value.red < blackthreshold and value.green < blackthreshold and value.blue < blackthreshold:
                colors.append('black')
            else:
                colors.append('white')
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
                self.rightMotorStep()
            elif currentColor == 'white':
                self.leftMotorStep()
            elif currentColor == 'red':
                print 'destination reached'
                return
            time.sleep(0.1)

    def followBlackWithTwoSensors(self):
        startTime = time.clock()
        self.decisionLog = []
        self.turnLog = []
        leftMortor = self.motors[0]
        rightMotor = self.motors[1]
        while 1:
            colors = self.getCurrentColor()
            leftColor = colors[0]
            rightColor = colors[1]
            self.colorLog.append((leftColor, rightColor))
            print leftColor + ' : ' + rightColor
            if leftColor == 'red' or rightColor == 'red':
                self.stop()
                self.decisionLog.append('end')
                elapsed = time.clock() - startTime
                self.turnLog.append((elapsed, 'end'))
                self.saveLog()
                print 'goal reached'
                return
            elif leftColor == 'white' and rightColor == 'white':
                preColor = self.colorLog[-2]
                if preColor[0] == 'black' and preColor[1] == 'black':
                    self.stop()
                    self.moveOneStep(-1, self.runPower, 0.2)
                    startTime = time.clock()
                    self.decisionLog.append('back')
                    #time.sleep(0.1)
                else:
                    self.move(self.runPower)
                    self.decisionLog.append('move')
            elif leftColor == 'white' and rightColor == 'black':
                self.stop()
                if len(self.decisionLog) >= 2 and (self.decisionLog[-1] in ['right', 'turnRight'] or self.decisionLog[-2] == ['right', 'turnRight']):# and self.decisionLog[-2] == 'right':      # make a huge turn at the conner
                    self.turnRight(self.bigTurnDegree)
                    self.decisionLog.append('turnRight')
                    elapsed = time.clock() - startTime
                    startTime = time.clock()
                    if elapsed > self.minimumElapse:
                        self.turnLog.append((elapsed, 'turnRight'))
                        print str(elapsed) + 'turn right at corner'
                else:
                    self.rightMotorStep(-1)
                    self.leftMotorStep()
                    self.decisionLog.append('right')
                time.sleep(0.1)
            elif leftColor == 'black' and rightColor == 'white':
                self.stop()
                if len(self.decisionLog) >= 2 and (self.decisionLog[-1] in ['left', 'turnLeft'] or self.decisionLog[-2] in ['left', 'turnLeft']): #and self.decisionLog[-2] == 'left':        # make a huge turn at the conner
                    self.turnLeft(self.bigTurnDegree)
                    self.decisionLog.append('turnLeft')
                    elapsed = time.clock() - startTime
                    startTime = time.clock()
                    if elapsed > self.minimumElapse:
                        self.turnLog.append((elapsed, 'turnLeft'))
                        print  str(elapsed) + 'turn left at corner'
                else:
                    self.leftMotorStep(-1)
                    self.rightMotorStep()
                    self.decisionLog.append('left')
                time.sleep(0.1)
            elif leftColor == 'black' and rightColor == 'black':
                self.stop()

                if self.decisionLog[-1] == 'move' or self.decisionLog[-1] == 'back':
                    self.moveOneStep(-1)
                    self.decisionLog.append('back')
                elif self.decisionLog[-1] == 'left':
                    self.turnLeft(self.bigTurnDegree)
                    self.decisionLog.append('turnLeft')
                elif self.decisionLog[-1] == 'right':
                    self.turnRight(self.bigTurnDegree)
                    self.decisionLog.append('turnRight')
                time.sleep(0.1)
            else:
                self.stop()
                print 'condition unhandled'
                break
            #time.sleep(0.1)                 # hold for a moment after each move


    def rightMotorStep(self, direction = 1, power = 70, runTime = 0.1):
        scale = (1 if direction == 1 else -1)
        mRight = self.motors[1]
        mRight.run(power * scale)
        time.sleep(runTime)
        mRight.brake()


    def leftMotorStep(self, direction = 1, power = 70, runTime = 0.1):
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

    def turnLeft(self, degrees = 0):
        leftMotor = self.motors[0]
        rightMotor = self.motors[1]
        self.leftMotorStep(-1)
        #leftMotor.turn(-1 * self.runPower, degrees)
        rightMotor.turn(self.turnPower, degrees)


    def turnRight(self, degrees = 0):
        leftMotor = self.motors[0]
        rightMotor = self.motors[1]
        self.rightMotorStep(-1)
        #rightMotor.turn(-1 * self.turnPower, degrees)
        leftMotor.turn(self.runPower, degrees)


    def drawMap(self, scale = 1.0 ):
        for log in self.turnLog:
            runTime = log[0]
            print runTime*scale
            action = log[1]
            self.move()
            time.sleep(runTime*scale)
            self.stop()
            print action
            if action == 'end':
                break
            self.turnWithAxis(290, action, self.penAxis)            # use 320 without a pen

            self.stop()
            time.sleep(1)
        print 'draw map finished'

    def turnWithAxis(self, degrees, action, axis):
        leftMotor = self.motors[0]
        rightMotor = self.motors[1]
        if axis == 'rightMotor':
            if action == 'turnLeft':
                leftMotor.turn(-1 * self.runPower, degrees)
            elif action == 'turnRight':
                leftMotor.turn(self.runPower,degrees)
        elif axis == 'leftMotor':
            if action == 'turnLeft':
                rightMotor.turn(self.runPower, degrees)
            elif action == 'turnRight':
                rightMotor.turn(-1 * self.runPower, degrees)
        else:
            print 'command error'

    def readTurnFromLog(self):
        file = open(self.turnLogFileName)
        lines = file.readlines()
        self.turnLog = []
        for line in lines:
            temp = line.split(':')
            runTime = float(temp[0])
            action = temp[1]
            action = action.strip('\n')
            self.turnLog.append((runTime, action))
        file.close()

    def saveLog(self):
        file = open(self.decisionLogFileName, 'w')
        for log in self.decisionLog:
            file.write(log + '\n')
        file.close()
        file = open(self.turnLogFileName, 'w')
        for log in self.turnLog:
            file.write(str(log[0]) + ':' + log[1] + '\n')
        file.close()






