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

    log_f = "track.log"

    # get lego
    brick = nxt.find_one_brick()

    # get motors
    motor = [nxt.Motor(brick, nxt.PORT_A), nxt.Motor(brick, nxt.PORT_B)]

    # get sensors
    sensors = [Colorv2(brick, PORT_1), Colorv2(brick, PORT_4)]
    sensors[0].debug = False
    sensors[1].debug = False

    def stop(): # brake the motors
        motor[0].brake() # not sync, errors may accumulate
        motor[1].brake()

    def self_turn(direction, power, period): # sensor in front of left wheel, self-turn means only turning right wheel
        motor[1].run(direction * power)

    def try_and_turn(direction, power, period, limit):
        """
        direction == False -> ccw and cw
        direction == True -> cw and ccw
        """
        
        first_dir = -1 if direction == False else 1
        second_dir = 1 if direction == False else -1

        # <----
        # ---->
        #      ---->
        #      <----
        for i in range(limit): # one dire
            if get_sensor_rgb(sensors[0]) == 'black' or get_sensor_rgb(sensors[0]) == 'red':
                stop()
                return (i+1) * first_dir
            self_turn(first_dir, power, period)
        # stop()

        for i in range(limit): # back and the other dir
            if get_sensor_rgb(sensors[0]) == 'black' or get_sensor_rgb(sensors[0]) == 'red':
                stop()
                return (i+1) * second_dir
            self_turn(second_dir, power, period)
        stop() # add this stop(brake) to make the inertia the same

        for i in range(limit): # back and the other dir
            if get_sensor_rgb(sensors[0]) == 'black' or get_sensor_rgb(sensors[0]) == 'red':
                stop()
                return (i+limit+1) * second_dir
            self_turn(second_dir, power, period)
        # stop()

        for i in range(limit): # one dire more
            if get_sensor_rgb(sensors[0]) == 'black' or get_sensor_rgb(sensors[0]) == 'red':
                stop()
                return (i+1) * first_dir
            self_turn(first_dir, power, period)
        stop()

        return None # no detection of black

    def move(power, run_time, direction):
        scale = (1 if direction == 1 else -1)
        print "move {0}".format("backward" if direction == 0 else "forward")
        motor[0].run(scale * power)
        motor[1].run(scale * power)

    cmd = raw_input("""Command ("1" for line-following, "2" for re-drawing map)>""")
    if cmd == "2":
        f = open(log_f, "r")
        for line in f:
            biubiu = line.strip('\n').split(' ')
            if biubiu[0] == 'move':
                move(int(biubiu[1]), float(biubiu[2]), int(biubiu[3]))
                time.sleep(float(biubiu[2]))
                stop()
                print 'move', int(biubiu[1]), float(biubiu[2]), int(biubiu[3])
            elif biubiu[0] == 'turn':
                stop()
                kaka = float(biubiu[2])
                times = kaka / 0.18
                times = int(times)
                for i in range(times):
                    self_turn(-1 if kaka < 0 else 1, int(biubiu[1]), abs(kaka))
                    time.sleep(float(biubiu[1]))
                    stop()
                print 'turn', -1 if kaka < 0 else 1, int(biubiu[1]), abs(kaka)
            else:
                stop()
        f.close()
    else:

        f = open(log_f, "w")
        # set conf
        move_power = 80
        turn_power = 70 
        detect_power = 80
        move_time = 0.2
        detect_time = 0.01

        count = 0
        running = False

        update_limit = 5
        update_step = 5 # seem like iterative deepening search
        turn = None # try_and_turn return value
        turned = False # last step, turned or not

        while True:
            color = get_sensor_rgb(sensors[0])
            print 'update_limit: ', update_limit
            print 0, color
            if color == 'red': # time to stop? or the first time?
                if running == False:
                    move(move_power, 0.1, 1) # first trigger
                    print >> f, "move", move_power, 0.1, 1
                    running = True
                else:
                    stop()
                    print >> f, "exit"
                    print 'red and exit'
                    break

            elif color == 'black':
                print 'black and go'
                if turned == True: # after try_an_turn, move forward carefully
                    print >> f, "move", move_power, 0.01, 1
                    move(move_power, 0.01, 1)
                else:
                    print >> f, "move", move_power, 0.05, 1
                    move(move_power, 0.05, 1)
                turned = False

            elif color == 'white':
                stop()
                turn = try_and_turn(True, detect_power, detect_time, update_limit)
                print 'turn', turn
                if turn != None:
                    print >> f, "turn", detect_power, detect_time * turn
                    update_limit = 5
                    turned = True
                    turn = None
                else:
                    update_limit += update_step
                print 'white and turn'
            else:
                stop()
                turn = try_and_turn(False, detect_power, detect_time, update_limit)
                print 'turn', turn
                if turn != None:
                    print >> f, "turn", detect_power, detect_time * turn
                    update_limit = 5
                    turned = True
                    turn = None
                else:
                    update_limit += update_step
                print 'other and c-turn'
        f.close()
