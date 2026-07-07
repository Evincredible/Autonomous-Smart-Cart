from gpiozero import Motor, PWMOutputDevice
from time import sleep

# Motor A (Left)
motor_left = Motor(forward=24, backward=23)
ena = PWMOutputDevice(25)

# Motor B (Right)
motor_right = Motor(forward=17, backward=27)
enb = PWMOutputDevice(22)

speed = 0.6   # 0.0 to 1.0

def set_speed(val):
    ena.value = val
    enb.value = val

set_speed(speed)

print("""
Controls:
f - forward
b - backward
l - left
r - right
s - stop
1 - low speed
2 - medium speed
3 - high speed
e - exit
""")

while True:
    cmd = input("Enter command: ").lower()

    if cmd == 'f':
        motor_left.forward()
        motor_right.forward()

    elif cmd == 'b':
        motor_left.backward()
        motor_right.backward()

    elif cmd == 'l':
        motor_left.stop()
        motor_right.forward()

    elif cmd == 'r':
        motor_left.forward()
        motor_right.stop()

    elif cmd == 's':
        motor_left.stop()
        motor_right.stop()

    elif cmd == '1':
        set_speed(0.3)
        print("Low speed")

    elif cmd == '2':
        set_speed(0.6)
        print("Medium speed")

    elif cmd == '3':
        set_speed(0.9)
        print("High speed")

    elif cmd == 'e':
        motor_left.stop()
        motor_right.stop()
        break

    else:
        print("Invalid command")
