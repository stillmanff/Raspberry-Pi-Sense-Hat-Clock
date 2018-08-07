#!/usr/bin/env python

from sense_hat import SenseHat
import time
from time import sleep

sense = SenseHat()

number = [
0,1,1,1, #zero
0,1,0,1,
0,1,0,1,
0,1,1,1,
0,0,1,0, #one
0,1,1,0,
0,0,1,0,
0,1,1,1,
0,1,1,1, #two
0,0,1,1,
0,1,1,0,
0,1,1,1,
0,1,1,1, #three
0,0,1,1,
0,0,1,1,
0,1,1,1,
0,1,0,1, #four
0,1,1,1,
0,0,0,1,
0,0,0,1,
0,1,1,1, #five
0,1,1,0,
0,0,1,1,
0,1,1,1,
0,1,0,0, #six
0,1,1,1,
0,1,0,1,
0,1,1,1,
0,1,1,1, #seven
0,0,0,1,
0,0,1,0,
0,1,0,0,
0,1,1,1, #eight
0,1,1,1,
0,1,1,1,
0,1,1,1,
0,1,1,1, #nine
0,1,0,1,
0,1,1,1,
0,0,0,1
]

blank = [
0,0,0,0,
0,0,0,0,
0,0,0,0,
0,0,0,0
]


twelvehour = True
blinkingSecond = True

hourColour   = [255,0,0] # red
minuteColour = [0,255,255] # cyan
empty        = [0,0,0] # off / black
white        = [255,255,255] # white
clockImage = [
0,0,0,0,0,0,0,0,
0,0,0,0,0,0,0,0,
0,0,0,0,0,0,0,0,
0,0,0,0,0,0,0,0,
0,0,0,0,0,0,0,0,
0,0,0,0,0,0,0,0,
0,0,0,0,0,0,0,0,
0,0,0,0,0,0,0,0
]

if twelvehour:
        print '12 hour mode'
else:
        print '24 hour mode'
if blinkingSecond:
        print 'Blinking seconds enabled'
else:
        print 'Blinking seconds disabled'
                

while True:
	hour = time.localtime().tm_hour
        if twelvehour:
                if hour > 12:
                        hour = hour - 12
                if hour == 0:
                        hour = 12
#        hour = hour + 2     #Debug adjustment - remove this
	minute = time.localtime().tm_min

	# Map digits to clockImage array

	pixelOffset = 0
	index = 0
	for indexLoop in range(0, 4):
		for counterLoop in range(0, 4):
			if (hour >= 10):
				clockImage[index] = number[int(hour/10)*16+pixelOffset]
                        else:
                                clockImage[index] = blank
			clockImage[index+4] = number[int(hour%10)*16+pixelOffset]
			clockImage[index+32] = number[int(minute/10)*16+pixelOffset]
			clockImage[index+36] = number[int(minute%10)*16+pixelOffset]
			pixelOffset = pixelOffset + 1
			index = index + 1
		index = index + 4

	# Colour the hours and minutes

	for index in range(0, 64):
		if (clockImage[index]):
                        if index < 32:
				clockImage[index] = hourColour
			else:
				clockImage[index] = minuteColour
		else:
			clockImage[index] = empty

        # Clear the leading hour if zero
        if (hour < 10):
                for outerIndex in range (0,25,8):
                        for indexLoop in range (0,4):
                                clockImage[indexLoop + outerIndex] = empty
                        

	# Display the time

	sense.set_rotation(180) # Optional
	sense.low_light = True # Optional
        if blinkingSecond:
                clockImage[0] = white
                sense.set_pixels(clockImage)
                sleep(1)
                clockImage[0] = empty
                sense.set_pixels(clockImage)
                sleep(1)
        else:
                sense.set_pixels(clockImage)
                sleep(2)
        
