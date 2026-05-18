#!/usr/bin/env python3
import rospy
import actionlib
from geometry_msgs.msg import Twist
from std_msgs.msg import Empty
from ardrone_action_pkg.msg import DroneCommandAction, DroneCommandFeedback, DroneCommandResult
import threading
FEEDBACK_RATE = 1.0
LANDING_DURATION = 3.0
TAKEOFF_BURST = 3
class DroneActionServer(object):
    def __init__(self):
        self._takeoff_pub = rospy.Publisher('/takeoff', Empty, queue_size=10)
        self._land_pub    = rospy.Publisher('/land', Empty, queue_size=10)
        self._cmd_pub     = rospy.Publisher('/cmd_vel', Twist, queue_size=10)
        self._state = 'LANDED'
        self._lock  = threading.Lock()
        self._feedback = DroneCommandFeedback()
        self._result   = DroneCommandResult()
        self._server = actionlib.SimpleActionServer(
            'drone_command',
            DroneCommandAction,
            execute_cb=self._handle_drone_command,
            auto_start=False,
        )
        self._server.start()
        rospy.loginfo('DroneActionServer is ready: astept goal.')
    def _publish_empty(self, pub, bursts):
        for _ in range(bursts):
            pub.publish(Empty())
            rospy.sleep(0.1)
    def _stop_motion(self):
        self._cmd_pub.publish(Twist())
    def _do_takeoff(self):
        with self._lock:
            self._state = 'FLYING'
        rospy.loginfo('Ciocanim spre ceruri (TAKEOFF burst x%d)' % TAKEOFF_BURST)
        self._publish_empty(self._takeoff_pub, TAKEOFF_BURST)
        rospy.loginfo('Drone airborne, streaming TAKEOFF feedback.')
        rate = rospy.Rate(1.0 / FEEDBACK_RATE)
        while not rospy.is_shutdown():
            if self._server.is_preempt_requested():
                rospy.loginfo('TAKEOFF preempted by client.')
                with self._lock:
                    self._state = 'LANDED'
                return False
            self._feedback.current_action = 'TAKEOFF'
            self._server.publish_feedback(self._feedback)
            with self._lock:
                if self._state != 'FLYING':
                    break
            rate.sleep()
        return True
    def _do_land(self):
        with self._lock:
            self._state = 'LANDING'
        rospy.loginfo('Coboram inapoi pe pamant (LAND burst x%d)' % TAKEOFF_BURST)
        self._publish_empty(self._land_pub, TAKEOFF_BURST)
        self._stop_motion()
        elapsed = 0.0
        rate = rospy.Rate(1.0 / FEEDBACK_RATE)
        while elapsed < LANDING_DURATION and not rospy.is_shutdown():
            if self._server.is_preempt_requested():
                rospy.loginfo('LAND preempted by client.')
                return False
            self._feedback.current_action = 'LANDING'
            self._server.publish_feedback(self._feedback)
            rate.sleep()
            elapsed += FEEDBACK_RATE
        with self._lock:
            self._state = 'LANDED'
        return True
    def _handle_drone_command(self, goal):
        cmd = goal.command.upper()
        rospy.loginfo('Request received command=%s' % cmd)
        if cmd not in ('TAKEOFF', 'LAND'):
            rospy.logwarn('Rejected unknown command: %s' % goal.command)
            self._result.message = 'unknown command'
            self._server.set_aborted(self._result)
            return
        try:
            if cmd == 'TAKEOFF':
                ok = self._do_takeoff()
            else:
                ok = self._do_land()
            if ok:
                rospy.loginfo('%s completed successfully!' % cmd)
                self._result.message = '%s done.' % cmd
                self._server.set_succeeded(self._result)
            else:
                rospy.loginfo('%s aborted.' % cmd)
                self._result.message = '%s cancelled.' % cmd
                self._server.set_preempted(self._result)
        except Exception as exc:
            rospy.logerr('Error during %s: %s' % (cmd, exc))
            self._stop_motion()
            self._result.message = '%s failed.' % cmd
            self._server.set_aborted(self._result)
def main():
    rospy.init_node('drone_action_server')
    DroneActionServer()
    try:
        rospy.spin()
    except KeyboardInterrupt:
        rospy.loginfo('Server interrupted.')
if __name__ == '__main__':
    main()
