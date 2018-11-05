#!/usr/bin/env python

from sense_hat import SenseHat
import time
from random import random
from time import sleep

sense = SenseHat()

def mToi(pValue):
    answer = pValue * 0.0295301
    return answer

def initBarometer(baromArr, baromInt):
    currentPressure = int(mToi(sense.get_pressure()) * 100) / 100.
    i = int(baromInt) + 1       #Initialize the array to the number of one-second slots we'll need
    baromArr = [currentPressure] * i
    return baromArr

def shiftPressures(baromArr, currPress):     #shift all historic barometer values to the left
    for i in range (1, len(baromArr)):
        baromArr[i - 1] = baromArr[i]
    baromArr[len(baromArr) - 1] = currPress
    return baromArr

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
blinkingBarometer = True
barometerInterval = 1800   # Update barometer value in seconds - twice per hour seems like a good interval
barometerTimer = 0      #Initialize counter
currentPressure = int(mToi(sense.get_pressure()) * 100) / 100.

pressureArray = []                                              #Define array for barometric pressure - will be a sliding window that updates every minute
pressureArray = initBarometer(pressureArray, barometerInterval) #Start with the same value every minute. Eventually we'll be able to look back once a minute to the value a barometerInterval ago.
#print pressureArray, len(pressureArray)

hourColour   = [255,0,0] # red
minuteColour = [0,255,255] # cyan
empty        = [0,0,0] # off / black
white        = [255,255,255] # white
green        = [0,255,0]     # green
red          = [255,0,0]     # red
dotColor = white  #assume initial stable barometric pressure

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
        if blinkingBarometer:
                print 'Barometer color enabled'
        else:
                print 'Barometer color disabled'
else:
        print 'Blinking seconds disabled'
                

while True:
	hour = time.localtime().tm_hour
        if twelvehour:
                if hour > 12:
                        hour = hour - 12
                if hour == 0:
                        hour = 12
	minute = time.localtime().tm_min
#        minute = minute + 4     #Debug adjustment - remove this

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
#                barometerTimer = barometerTimer + 1
#                if barometerTimer >= barometerInterval:      #get ready to update the barometer dot color
#                        barometerTimer = 0                   #reinitialize
#                        oldPressure = currentPressure
                currentPressure = int(mToi(sense.get_pressure()) * 100) / 100.   #make sure the change is significant - two decimal places
                pressureArray = shiftPressures(pressureArray, currentPressure)                  #put the new pressure at the end of the array
                oldPressure = pressureArray[0]                                  #look back as far as possible
#                print oldPressure, currentPressure, pressureArray
#                currentPressure = currentPressure * (random() + 0.5)
#                print oldPressure, currentPressure
                if oldPressure > currentPressure:
                    dotColor = red          #pressure falling
                elif oldPressure < currentPressure:
                    dotColor = green        #Pressure rising
                else:
                    dotColor = white        #Pressure steady (within margin of error)
                clockImage[0] = dotColor
                sense.set_pixels(clockImage)
                sleep(1)
                clockImage[0] = empty
                sense.set_pixels(clockImage)
                sleep(1)
        else:
                sense.set_pixels(clockImage)
                sleep(2)
        
