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

    def getCurrentColor(self, cSensor):
        value = cSensor.get_sample()

        # print 'number: ', value.number,
        # print ', red: ', value.red,
        # print ', green: ', value.green,
        # print ', blue: ', value.blue,
        # print ', white: ', value.white,
        # print ', index: ', value.index,
        # print ', |red|: ', value.normred,
        # print ', |green|: ', value.normgreen,
        # print ', |blue|: ', value.normblue

        if value.white > 100:
            return 'white'
        elif value.red < 50 and value.green < 50 and value.blue < 50:
            return 'black'
        elif value.normred == 255:
            return 'red'
        else:
            return 'otherColor'

    def move(self, power = 60, direction = 1):       # move forward or backward
        scale = (1 if direction == 1 else -1)
        self.motors[0].run(scale * power)
        self.motors[1].run(scale * power)

    def turn(self, direction):
        mLeft = self.motors[0]
        mRight = self.motors[1]
        if direction == 'W':
            mLeft.turn(60, 100)
            mLeft.turn(-60, 100)
            mRight.turn(60, 100)
            mRight.turn(-60, 100)


    def moveOneStep(self, power = 70, direction = 1, runTime = 0.15):       # move forward or backward
        scale = (1 if direction == 1 else -1)
        self.motors[0].run(scale * power)
        self.motors[1].run(scale * power)
        time.sleep(runTime)
        self.motors[0].brake()
        self.motors[1].brake()
        pass

    def stop(self):
        for motor in self.motors:
            motor.brake()

    def followBlackWithOneSensor(self):
        while 1:
            currentColor = self.getCurrentColor(self.colorSensors[0])
            print currentColor
            if currentColor == 'black':
                self.moveRightLeg()
            elif currentColor == 'white':
                self.moveLeftLeg()
            elif currentColor == 'red':
                print 'destination reached'
                return
            time.sleep(0.1)

    def followBlackWithTwoSensors(self):
        leftColorSensor = self.colorSensors[0]
        rightColorSensor = self.colorSensors[1]

        while 1:
            leftColor = self.getCurrentColor(leftColorSensor)
            rightColor = self.getCurrentColor(rightColorSensor)
            print leftColor + ' : ' + rightColor
            # if leftColor == 'red' or rightColor == 'red'
            #     print 'goal reached'
            #     return
            if leftColor == 'white' and rightColor == 'white':
                self.moveOneStep()
            elif leftColor == 'black' and rightColor == 'white':
                self.stop()
                self.moveRightLeg()
            elif leftColor == 'white' and leftColor == 'black':
                self.stop()
                self.moveLeftLeg()
            time.sleep(0.1)


    def moveRightLeg(self, power = 70, runTime = 0.1):
        mRight = self.motors[1]
        mRight.run(power)
        time.sleep(runTime)
        mRight.brake()


    def moveLeftLeg(self, power = 70, runTime = 0.1):
        mleft = self.motors[0]
        mleft.run(power)
        time.sleep(runTime)
        mleft.brake()
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





