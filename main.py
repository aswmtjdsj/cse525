import nxt, time, random
from nxt.sensor import *
from nxt.sensor.hitechnic import *

def get_sensor_rgb(color_sensor):
    value = color_sensor.get_sample()
    if color_sensor.debug == True:
        print 'number: ', value.number,
        print ', red: ', value.red,
        print ', green: ', value.green,
        print ', red: ', value.blue,
        print ', white: ', value.white,
        print ', index: ', value.index,
        print ', |red|: ', value.normred,
        print ', |green|: ', value.normgreen,
        print ', |blue|: ', value.normblue
    return value.normred, value.normgreen, value.normblue

def rgb_is_black(color_value):
    return color_value[0] < 20 and color_value[1] < 20 and color_value[2] < 20

def rgb_is_white(color_value):
    return color_value[0] > 220 and color_value[1] > 220 and color_value[2] > 220

def rgb_is_red(color_value):
    return color_value[0] > 200 and color_value[1] < 100 and color_value[2] < 100

if __name__ == '__main__':

    # get lego
    brick = nxt.find_one_brick()

    # get motors
    motor = [nxt.Motor(brick, nxt.PORT_A), nxt.Motor(brick, nxt.PORT_B)]

    # light = Light(brick, PORT_1)
    # color = Color20(brick, PORT_1)
    # color sensor v2
    sensors = [Colorv2(brick, PORT_1), Colorv2(brick, PORT_4)]
    sensors[0].debug = False
    sensors[1].debug = False
    move_power = 100
    turn_power = 70
    move_time = 0.2
    turn_time = 0.1

    def move(power, run_time, direction):
        scale = (1 if direction == 1 else -1)
        print "move {0}".format("forward" if direction == 0 else "backward")
        motor[0].run(scale * power)
        motor[1].run(scale * power)
        time.sleep(run_time)
        motor[0].brake()
        motor[1].brake()

    def turn(direction, scale):
        if direction == 'NE':
            pass
        elif direction == 'SE':
            pass
        elif direction == 'SW':
            pass
        elif direction == 'NW':
            pass
        else:
            print 'wrong direction'

    count = 0
    running = True
    while running:
        # sense
        # light.set_illuminated(False)
        # print 'light: ', light.get_sample()
        # print 'light color: ', color.get_light_color()
        # print 'reflected light: ', color.get_reflected_light(Type.COLORRED)
        # print 'color: ', color.get_color()
        count += 1

        # run
        move(100, 0.2, 1)
        for i in range(10):
            motor[0].run(-80)
            motor[1].run(80)
            time.sleep(0.05)
            motor[0].brake()
            motor[1].brake()

        for i, sensor in enumerate(sensors):
            color = get_sensor_rgb(sensor)
            time.sleep(0.5)
            print i, 
            if rgb_is_black(color) == True:
                print 'black'
            elif rgb_is_white(color) == True:
                print 'white'
            elif rgb_is_red(color) == True:
                print 'red and exit'
                running = False
            else:
                print 'other'

        # # turn
        # m_id = random.randint(0, 1)
        # motor[m_id].run(100)
        # time.sleep(0.5)
        # motor[m_id].brake()
        # time.sleep(1)
