#!/usr/bin/env python3

import rospy
from geometry_msgs.msg import Twist
from std_msgs.msg import String

class MovePub:
    def _init_(self):
        rospy.init_node('motor_node')
        self.pub = rospy.Publisher('/cmd_vel', Twist, queue_size=10)
        self.sub = rospy.Subscriber('/robot_decision', String, self.decision_cb)
        self.move = Twist()

    def decision_cb(self, msg):
        self.move.linear.x = 0.0
        self.move.angular.z = 0.0
        
        if msg.data == "forward":
            self.move.linear.x = 0.5
        elif msg.data == "turn_left":
            self.move.angular.z = 0.5
        elif msg.data == "turn_right":
            self.move.angular.z = -0.5
            
        self.pub.publish(self.move)

if _name_ == '_main_':
    MovePub()
    rospy.spin()
