#!/usr/bin/env python3
import rospy
import actionlib
from ardrone_action_pkg.msg import DroneCommandAction, DroneCommandGoal
import sys
class DroneActionClient(object):
    def __init__(self):
        self._client = actionlib.SimpleActionClient('drone_command', DroneCommandAction)
    def send_goal(self, command):
        rospy.loginfo('Astept action server...')
        self._client.wait_for_server()
        goal = DroneCommandGoal()
        goal.command = command.upper()
        rospy.loginfo('Sending goal: %s' % goal.command)
        self._client.send_goal(goal, feedback_cb=self._handle_feedback, done_cb=self._handle_done)
    def _handle_feedback(self, feedback_msg):
        rospy.loginfo('[FEEDBACK] current_action=%s' % feedback_msg.current_action)
    def _handle_done(self, state, result):
        rospy.loginfo('[RESULT] %s' % result.message)
        rospy.signal_shutdown('done')
def main():
    if len(sys.argv) < 2 or sys.argv[1].upper() not in ('TAKEOFF', 'LAND'):
        print('Usage: drone_action_client.py <TAKEOFF|LAND>')
        sys.exit(1)
    rospy.init_node('drone_action_client')
    client = DroneActionClient()
    client.send_goal(sys.argv[1])
    try:
        rospy.spin()
    except KeyboardInterrupt:
        rospy.loginfo('Client interrupted.')
if __name__ == '__main__':
    main()
