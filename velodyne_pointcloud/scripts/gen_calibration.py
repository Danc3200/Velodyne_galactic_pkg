#!/usr/bin/python
# Software License Agreement (BSD License)
#
# Copyright (C) 2012, Austin Robot Technology
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above
#    copyright notice, this list of conditions and the following
#    disclaimer in the documentation and/or other materials provided
#    with the distribution.
#  * Neither the name of Austin Robot Technology, Inc. nor the names
#    of its contributors may be used to endorse or promote products
#    derived from this software without specific prior written
#    permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
# Revision $Id$

"""
Generate YAML calibration file from Velodyne db.xml.

The input data provided by the manufacturer are in degrees and
centimeters. The YAML file uses radians and meters, following ROS
standards [REP-0103].

"""

from __future__ import print_function

import math
import optparse
import os
import sys
from xml.etree import ElementTree
import yaml

# parse the command line
usage = """usage: %prog infile.xml [outfile.yaml]

       Default output file is input file with .yaml suffix."""
parser = optparse.OptionParser(usage=usage)
options, args = parser.parse_args()

if len(args) < 1:
    parser.error('XML file name missing')
    sys.exit(9)

xmlFile = args[0]
if len(args) >= 2:
    yamlFile = args[1]
else:
    yamlFile, ext = os.path.splitext(xmlFile)
    yamlFile += '.yaml'

print('converting "' + xmlFile + '" to "' + yamlFile + '"')

calibrationGood = True
def xmlError(msg):
    'handle XML calibration error'
    global calibrationGood
    calibrationGood = False
    print('gen_calibration.py: ' + msg)

db = None
try:
    db = ElementTree.parse(xmlFile)
except IOError:
    xmlError('unable to read ' + xmlFile)
except ElementTree.ParseError:
    xmlError('XML parse failed for ' + xmlFile)

if not calibrationGood:
    sys.exit(2)

# create a dictionary to hold all relevant calibration values
calibration = {'num_lasers': 0, 'pitch': 0.0, 'roll': 0.0, 'lasers': []}
cm2meters = 0.01                       # convert centimeters to meters

def addLaserCalibration(laser_num, key, val):
    'Define key and corresponding value for laser_num'
    global calibration
    if laser_num < len(calibration['lasers']):
        calibration['lasers'][laser_num][key] = val
    else:
        calibration['lasers'].append({key: val})

# add minimum laser intensities
minIntensities = db.find('DB/minIntensity_')
if minIntensities != None:
    index = 0
    for el in minIntensities:
        if el.tag == 'count':
            calibration['num_lasers'] = int(el.text)
        elif el.tag == 'item':
            addLaserCalibration(index, 'min_intensity', float(el.text))
            index += 1

# add maximum laser intensities
maxIntensities = db.find('DB/maxIntensity_')
if maxIntensities != None:
    index = 0
    for el in maxIntensities:
        if el.tag == 'count':
            calibration['num_lasers'] = int(el.text)
        elif el.tag == 'item':
            addLaserCalibration(index, 'max_intensity', float(el.text))
            index += 1

# add calibration information for each laser
for el in db.find('DB/points_'):
    if el.tag == 'count':
        calibration['num_lasers'] = int(el.text)
    elif el.tag == 'item':
        for px in el:
            for field in px:
                if field.tag == 'id_':
                    index = int(field.text)
                    addLaserCalibration(index, 'laser_id', index)
                elif field.tag == 'rotCorrection_':
                    addLaserCalibration(index, 'rot_correction',
                                        math.radians(float(field.text)))
                elif field.tag == 'vertCorrection_':
                    addLaserCalibration(index, 'vert_correction',
                                        math.radians(float(field.text)))
                elif field.tag == 'distCorrection_':
                    addLaserCalibration(index, 'dist_correction', 
                                        float(field.text) * cm2meters)
                elif field.tag == 'distCorrectionX_':
                    addLaserCalibration(index, 'dist_correction_x',
                                        float(field.text) * cm2meters)
                elif field.tag == 'distCorrectionY_':
                    addLaserCalibration(index, 'dist_correction_y',
                                        float(field.text) * cm2meters)
                elif field.tag == 'vertOffsetCorrection_':
                    addLaserCalibration(index, 'vert_offset_correction',
                                        float(field.text) * cm2meters)
                elif field.tag == 'horizOffsetCorrection_':
                    addLaserCalibration(index, 'horiz_offset_correction',
                                        float(field.text) * cm2meters)
                elif field.tag == 'focalDistance_':
                    addLaserCalibration(index, 'focal_distance', 
                                        float(field.text) * cm2meters)
                elif field.tag == 'focalSlope_':
                    addLaserCalibration(index, 'focal_slope', float(field.text))

# validate input data
if calibration['num_lasers'] <= 0:
    xmlError('no lasers defined')
elif calibration['num_lasers'] != len(calibration['lasers']):
    xmlError('inconsistent number of lasers defined')

# TODO: make sure all required fields are present.
# (Which ones are required?)

if calibrationGood:

    # write calibration data to YAML file
    f = open(yamlFile, 'w')
    try:
        yaml.dump(calibration, f)
    finally:
        f.close()