#!/usr/bin/env python
import rospy
from sensor_msgs.msg import Joy

def Joycallback(data):
    rospy.loginfo(rospy.get_caller_id() + "I heard %s", data.data)
    
def func():
    rospy.init_node('red_ball', anonymous=True)

    rospy.Subscriber("/bluetooth_teleop/joy", Joy, Joycallback)

    # spin() simply keeps python from exiting until this node is stopped
    rospy.spin()

if __name__ == '__main__':
    func()
