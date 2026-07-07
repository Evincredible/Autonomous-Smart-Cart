#!/usr/bin/env python3

import serial
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

# Use by-path to reliably identify ESP32 (ttyUSB1 physical port)
SERIAL_PORT = '/dev/serial/by-path/platform-xhci-hcd.0-usb-0:2:1.0-port0'
BAUD_RATE = 115200

class CmdVelToSerial(Node):
    def __init__(self):
        super().__init__('cmd_vel_to_serial')
        self.ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        self.sub = self.create_subscription(
            Twist,
            '/cmd_vel',
            self.cmd_callback,
            10
        )
        self.get_logger().info(f'Opened serial port: {SERIAL_PORT}')

    def cmd_callback(self, msg):
        linear_x = msg.linear.x
        angular_z = msg.angular.z
        line = f"{linear_x:.3f},{angular_z:.3f}\n"
        self.ser.write(line.encode('utf-8'))
        self.get_logger().info(f"Sent: {line.strip()}")

def main():
    rclpy.init()
    node = CmdVelToSerial()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.ser.close()
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()