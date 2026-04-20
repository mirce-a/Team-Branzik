#!/usr/bin/env python3

import rospy
from sensor_msgs.msg import LaserScan
from std_msgs.msg import String

class ScanSub:
    def _init_(self):
        rospy.init_node('scanner_node')
        self.decision_pub = rospy.Publisher('/robot_decision', String, queue_size=10)
        self.sub = rospy.Subscriber('/scan', LaserScan, self.callback)

    def callback(self, msg):
        front = msg.ranges[len(msg.ranges) // 2]
        right = msg.ranges[0]
        left = msg.ranges[-1]
        
        decision = "forward"
        if front < 1.0 or right < 1.0:
            decision = "turn_left"
        elif left < 1.0:
            decision = "turn_right"
            
        self.decision_pub.publish(decision)

if _name_ == '_main_':
    ScanSub()
    rospy.spin()
