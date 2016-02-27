#!/usr/bin/env python
import rospy
import roslib
# OpenCV
import cv2
import numpy as np

from sensor_msgs.msg import Joy
from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist
from cv_bridge import CvBridge, CvBridgeError

#Global vars, horrible practice but this is small, demo code.
gogo = 0
cv_image = None


def Joycallback(data):
    global gogo
    gogo = data.buttons[11]
    #print gogo

def Imagecallback(data):
    global cv_image
    try:
        cv_image = CvBridge().imgmsg_to_cv2(data, "bgr8")
    except CvBridgeError as e:
        print(e)
    
def func():
    rospy.init_node('red_ball', anonymous=True)

    rospy.Subscriber("/bluetooth_teleop/joy", Joy, Joycallback)
    rospy.Subscriber("/usb_cam/image_raw", Image, Imagecallback)

    pub = rospy.Publisher('/cmd_vel', Twist, queue_size=1)

    rate = rospy.Rate(20) # 20hz
    cmd = Twist()
    redLower = (10,10,120)#(0, 255, 40)
    redUpper = (100,100,200)#(0, 255, 107)
    pts = (64)

    global cv_image
    
    print "Wait on first image"
    while cv_image is None:
        pass
    print "starting"

    while not rospy.is_shutdown():

        # Code takes image received, tries to face ball at distance of ~ 0.5m
        
        # blur image to remove sharp corners
        blurred = cv2.GaussianBlur(cv_image, (11, 11), 0)

        # construct mask, perform dilations and erosions to remove small blobs
        mask = cv2.inRange(blurred, redLower, redUpper)
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)

        # find contours in the mask and initialize the current
        # (x, y) center of the ball
        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
        center = None

        if len(cnts) > 0:     
            c = max(cnts, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            M = cv2.moments(c)
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

            # only proceed if the radius meets a minimum size
            if radius > 20:
                # draw the circle and centroid on the frame,
                # then update the list of tracked points
                cv2.circle(blurred, (int(x), int(y)), int(radius),(0, 255, 255), 2)
                cv2.circle(blurred, center, 5, (0, 0, 255), -1)

                #print center
                #print radius
                # We got the ball, calculate movement
                cmd.linear.x = (50.0 - radius)/100.0 #0.5m/s at extreme range
                cmd.angular.z = (320.0 - center[0])/640.0 # 0.5m/s at extreme offset
        else:
            cmd.linear.x = 0
            cmd.angular.z = 0 #Ensure no runaway
                
                
        #cv2.imshow("Image window", blurred)
        #cv2.waitKey(3)


        # Ensure ball following only works when deadman is held down
        if gogo == 1: pub.publish(cmd)

        rate.sleep()

if __name__ == '__main__':
    func()
