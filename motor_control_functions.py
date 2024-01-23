import PiMotor

# Control individual motors
m1 = PiMotor.Motor("MOTOR1", 1)
m2 = PiMotor.Motor("MOTOR2", 1)
# Control both motors
motorAll = PiMotor.LinkedMotors(m1, m2)


# Define motor control functions
def accelerate():
    motorAll.forward(100)
    return "accelerate"


def reverse():
    motorAll.reverse(100)
    return "reverse"


def left_turn():
    m1.forward(50)
    m2.forward(100)
    return "leftTurn"


def right_turn():
    m1.forward(100)
    m2.forward(50)
    return "rightTurn"


def left_in_place_turn():
    m1.forward(50)
    m2.reverse(50)
    return "leftInPlaceTurn"


def right_in_place_turn():
    m1.reverse(50)
    m2.forward(50)
    return "rightInPlaceTurn"


def stop():
    motorAll.stop()
    return "stop"
