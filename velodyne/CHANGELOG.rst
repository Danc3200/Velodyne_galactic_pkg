Change history
==============

1.0.0 (forthcoming)

 * Convert to catkin.
 * Release to Hydro.

0.9.1 (2012-06-05)
------------------

 * Only include "enabled" lasers in YAML calibration file.
 * Driver socket read path improvements.
 * New param subdirectory for parameter files.
 * Add launch file for the HDL-32E.
 * Add rviz_points.vcg file for viewing Velodyne point clouds with rviz.
 * Fix bug when reading configuration with default minIntensity.
 * Add unit tests with 32E data.
 * Released to Electric, Fuerte and Groovy.

0.9.0 (2012-04-03)
------------------

 * Completely revised API, anticipating a 1.0.0 release.
 * HDL-32E device support.
 * New YAML configuration file format.
 * New velodyne_driver and velodyne_pointcloud packages.
 * Old velodyne_common and velodyne_pcl packages no longer included.
 * Released to Electric, Fuerte and Groovy.

0.2.6 (2011-02-23)
------------------

 * Label all timing-dependent tests "realtime" so they do not run by
   default on the build farm machines.

0.2.5 (2010-11-19)
------------------

 * Initial implementation of new 0.3 interfaces.
 * Support for ROS 1.3 `std_msgs::Header` changes.

0.2.0 (2010-08-17)
------------------

 * Initial release to ROS C-turtle.