#!/usr/bin/env python3
import sys
import rclpy
from rclpy.node import Node
from square_mover.srv import MoveSquare


class SquareMoverClient(Node):
    def __init__(self):
        super().__init__('square_mover_client')
        self.declare_parameter('side', 1.0)
        self.declare_parameter('repetitions', 1)
        self.declare_parameter('easter_egg', 1101)
        self._client = self.create_client(MoveSquare, 'move_square')

    def _wait_for_server(self, timeout_sec: float = 5.0) -> bool:
        self.get_logger().info('Waiting for service /move_square …')
        ready = self._client.wait_for_service(timeout_sec=timeout_sec)
        if not ready:
            self.get_logger().error(
                f'Service /move_square not available after {timeout_sec:.0f} s. Is the server running?'
            )
        return ready

    def send_request(self) -> bool:
        if not self._wait_for_server():
            return False

        side = self.get_parameter('side').get_parameter_value().double_value
        repetitions = self.get_parameter('repetitions').get_parameter_value().integer_value
        easter_egg = self.get_parameter('easter_egg').get_parameter.value().integer_value
        req = MoveSquare.Request()
        req.side = side
        req.repetitions = repetitions
        req.easter_egg = easter_egg

        self.get_logger().info(f'Sending request — side={side:.2f} m, repetitions={repetitions}')

        future = self._client.call_async(req)
        rclpy.spin_until_future_complete(self, future)

        if future.result() is not None:
            success = future.result().success
            self.get_logger().info('Succes :)' if success else 'Not okay')
            return success
        else:
            self.get_logger().error(f'Am dat-o in bara undeva: {future.exception()}')
            return False


def main(args=None):
    rclpy.init(args=args)
    client = SquareMoverClient()
    try:
        success = client.send_request()
    finally:
        client.destroy_node()
        rclpy.shutdown()
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
