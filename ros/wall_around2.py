#!/usr/bin/env python
import rospy,copy,math
from geometry_msgs.msg import Twist
from std_srvs.srv import Trigger, TriggerResponse
from sensor_msgs.msg import Joy

class WallStop():
    def __init__(self):
        self.cmd_vel = rospy.Publisher('/cmd_vel',Twist,queue_size=1)

        rospy.Subscriber('/joy', Joy, self.callback_joy)

    def callback_joy(self,message):
        data = Twist() 
        data.linear.x = message.axes[1]
        data.angular.z = message.axes[0
        self.cmd_vel.publish(data)        
    
    def run(self):
        rate = rospy.Rate(20)
        data = Twist()

        while not rospy.is_shutdown():
            rate.sleep()

if __name__ == '__main__':
    rospy.init_node('wall_stop')
    rospy.wait_for_service('/motor_on')
    rospy.wait_for_service('/motor_off')
    rospy.on_shutdown(rospy.ServiceProxy('/motor_off',Trigger).call)
    rospy.ServiceProxy('/motor_on',Trigger).call()
    WallStop().run()


