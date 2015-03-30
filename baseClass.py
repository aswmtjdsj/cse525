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
        self.runPower = 70
        self.stepTime = 0.1
        self.penAxis = 'rightMotor'
        self.turnLogFileName = 'turnLog.txt'
        self.decisionLogFileName = 'decisionLog.txt'

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
                self.rightMotorStep()
            elif currentColor == 'white':
                self.leftMotorStep()
            elif currentColor == 'red':
                print 'destination reached'
                return
            time.sleep(0.1)

    def followBlackWithTwoSensors(self):
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
                self.move(self.runPower)
                self.decisionLog.append('move')
            elif leftColor == 'white' and rightColor == 'black':
                self.stop()
                if len(self.decisionLog) >= 2 and self.decisionLog[-1] == 'right' and self.decisionLog[-2] == 'right':      # make a huge turn at the conner
                    self.turnRight(70)
                    self.decisionLog.append('right')
                    elapsed = time.clock() - startTime
                    startTime = time.clock()
                    if elapsed > 0.1:
                        self.turnLog.append((elapsed, 'turnRight'))
                else:
                    self.leftMotorStep()
                    self.decisionLog.append('right')
                time.sleep(0.1)
            elif leftColor == 'black' and rightColor == 'white':
                self.stop()
                if len(self.decisionLog) >= 2 and self.decisionLog[-1] == 'left' and self.decisionLog[-2] == 'left':        # make a huge turn at the conner
                    self.turnLeft(70)
                    self.decisionLog.append('left')
                    elapsed = time.clock() - startTime
                    startTime = time.clock()
                    if elapsed > 0.1:
                        self.turnLog.append((elapsed, 'turnLeft'))
                else:
                    self.rightMotorStep()
                    self.decisionLog.append('left')
                time.sleep(0.1)
            elif leftColor == 'black' and rightColor == 'black':
                self.stop()
                self.moveOneStep()
            else:
                self.stop()
                print 'condition unhandled'
                break
            #time.sleep(0.1)                 # hold for a moment after each move
        self.saveLog()


    def rightMotorStep(self, direction = 1, power = 70, runTime = 0.2):
        scale = (1 if direction == 1 else -1)
        mRight = self.motors[1]
        mRight.run(power * scale)
        time.sleep(runTime)
        mRight.brake()


    def leftMotorStep(self, direction = 1, power = 70, runTime = 0.2):
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

    def turnLeft(self, degrees = 250):
        leftMotor = self.motors[0]
        rightMotor = self.motors[1]
        leftMotor.turn(-1 * self.runPower, degrees)
        rightMotor.turn(self.runPower, degrees)


    def turnRight(self, degrees = 250):
        leftMotor = self.motors[0]
        rightMotor = self.motors[1]
        rightMotor.turn(-1 * self.runPower, degrees)
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
            self.turnWithAxis(300, action, self.penAxis)
            #time.sleep(1)
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






