import nxt, time, random, math
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

    if value.white > 200 and value.normred > 200 and value.normgreen > 200 and value.normblue > 200:
        return 'white'
    elif value.normred == 255 and value.normgreen < 100 and value.normblue < 100:
        return 'red'
    elif value.red < 50 and value.green < 50 and value.blue < 50:
        return 'black'
    else:
        return 'other'

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
    move_power = 80
    detect_power = 80
    turn_power = 100
    move_time = 0.2
    turn_time = 0.1
    detect_time = 0.01

    def self_turn(direction, power, period):
        # motor[0].run(direction * power)
        motor[1].run(direction * power)
        # time.sleep(period)
        # motor[0].brake()
        # motor[1].brake()

    # def turn_right(direction, power, period):
    def turn_right(power, period):
        motor[0].run(power)
        time.sleep(period)
        motor[0].brake()
        motor[1].brake()

    # def turn_left(direction, power, period):
    def turn_left(power, period):
        # motor[1].run(direction * power)
        motor[1].run(power)
        time.sleep(period)
        motor[0].brake()
        motor[1].brake()

    def try_and_turn(direction, power, period, limit):
        """
        direction == False -> ccw and cw
        direction == True -> cw and ccw
        """
        
        first_dir = -1 if direction == False else 1
        second_dir = 1 if direction == False else -1
        for i in range(limit): 
            if get_sensor_rgb(sensors[0]) == 'black':
                return (i+1) * first_dir
            self_turn(first_dir, power, period)
        motor[0].brake()
        motor[1].brake()

        for i in range(limit):
            if get_sensor_rgb(sensors[0]) == 'black':
                return (i+1) * second_dir
            self_turn(second_dir, power, period)
        motor[0].brake()
        motor[1].brake()

        return None

    def move(power, run_time, direction):
        scale = (1 if direction == 1 else -1)
        print "move {0}".format("backward" if direction == 0 else "forward")
        motor[0].run(scale * power)
        motor[1].run(scale * power)
        time.sleep(run_time)
        motor[0].brake()
        motor[1].brake()

    count = 0
    running = True
    try_number = 0

    update_limit = 5
    update_step = 5
    turn = None
    turned = False
    while running:
        color = get_sensor_rgb(sensors[0])
        print 'update_limit: ', update_limit
        print 0, color
        # print 1, get_sensor_rgb(sensors[1])
        if color == 'red':
            print 'red and exit'
            break
        elif color == 'black':
            try_number = 0
            print 'black and go'
            if turned == True:
                move(move_power, 0.05 / 2., 1)
            else:
                move(move_power, 0.05, 1)
            turned = False
        elif color == 'white':
            turn = try_and_turn(True, detect_power, detect_time, update_limit)
            print 'turn', turn
            if turn != None:
                update_limit = 5
                if turn > 1:
                    turn_right(80, 0.01 * abs(turn))
                else:
                    turn_left(80, 0.01 * abs(turn))
                turned = True
                turn = None
            else:
                update_limit += update_step
            print 'white and turn'
        else:
            turn = try_and_turn(False, detect_power, detect_time, update_limit)
            print 'turn', turn
            if turn != None:
                update_limit = 5
                if turn > 1:
                    turn_right(80, 0.01 * abs(turn))
                else:
                    turn_left(80, 0.01 * abs(turn))
                turned = True
                turn = None
            else:
                update_limit += update_step
            print 'other and c-turn'