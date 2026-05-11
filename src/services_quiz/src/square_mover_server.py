#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from square_mover.srv import MoveSquare
import time
import math

LINEAR_SPEED = 0.2
ANGULAR_SPEED = 0.5
TURN_ANGLE = math.pi / 2.0


class SquareMoverServer(Node):
    def __init__(self):
        super().__init__('square_mover_server')
        self._cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self._srv = self.create_service(MoveSquare, 'move_square', self._handle_move_square)
        self.get_logger().info('SquareMoverServer is ready: astept request.')

    def _publish_twist(self, linear: float, angular: float):
        msg = Twist()
        msg.linear.x  = linear
        msg.angular.z = angular
        self._cmd_pub.publish(msg)

    def _drive_straight(self, side: float):
        duration = side / LINEAR_SPEED
        self.get_logger().info(f'Ciocanim spre ciocanesti {side:.2f} m ({duration:.2f}sec)')
        start = time.time()
        while time.time() - start < duration:
            self._publish_twist(LINEAR_SPEED, 0.0)
            time.sleep(0.05)
        self._stop()
        time.sleep(0.2)

    def _turn_90(self):
        duration = TURN_ANGLE / ANGULAR_SPEED
        self.get_logger().info(f'Turning 90 degrees  ({duration:.2f}sec)')
        start = time.time()
        while time.time() - start < duration:
            self._publish_twist(0.0, ANGULAR_SPEED)
            time.sleep(0.05)
        self._stop()
        time.sleep(0.2)

    def _stop(self):
        self._publish_twist(0.0, 0.0)

    def _handle_move_square(self, request, response):
        side        = request.side
        repetitions = request.repetitions
	easter_egg = request.easter_egg
        self.get_logger().info(f'Request received side={side:.2f}m, repetitions={repetitions}')

        if easter_egg == 1337:
            self.get_logger().info(f'You found the e4st3r 3gg...')	

        if side <= 0.0:
            self.get_logger().error(f'Invalid side len: {side}')
            response.success = False
            return response

        if repetitions <= 0:
            self.get_logger().error(f'Invalid reps: {repetitions}')
            response.success = False
            return response

        try:
            for rep in range(repetitions):
                self.get_logger().info(f'Starting square {rep + 1}/{repetitions}')
                for side_idx in range(4):
                    self.get_logger().info(f'  Side {side_idx + 1}/4')
                    self._drive_straight(side)
                    self._turn_90()
                self.get_logger().info(f'Completed square {rep + 1}/{repetitions}')

            self.get_logger().info('All reps completed successfully!')
            response.success = True

        except Exception as exc:
            self.get_logger().error(f'Error during movement: {exc}')
            self._stop()
            response.success = False

        return response


def main(args=None):
    rclpy.init(args=args)
    node = SquareMoverServer()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Server interrupted.')
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
