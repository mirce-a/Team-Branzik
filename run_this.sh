catkin_make
source devel/setup.bash

chmod +x src/ardrone_action_pkg/scripts/*.py

roslaunch ardrone_action_pkg drone_action.launch

rosrun ardrone_action_pkg drone_action_client.py TAKEOFF
rosrun ardrone_action_pkg drone_action_client.py LAND
