
#!/usr/bin/env python

from sense_hat import SenseHat
import time
from random import random
from time import sleep

sense = SenseHat()

#**********************************************************************************************************
#Parameters  - everything that might need to be changed is in this section.
activeTimeStartHour = 7
activeTimeStartMinute = 0
quietTimeStartHour = 22
quietTimeStartMinute = 0
clockAlwaysActive = False
dimDisplayHour = 19         #Controls for night mode on display.
brightDisplayHour = 7       #Future improvement: add formula to approximate sunset times, if needed.
dimDisplay = True           #Make display dimming an option
twelvehour = True
blinkingSecond = True
blinkingBarometer = True
orientation = 180               # default orientation is upside down (power cable on top). Can modify in lightLevel() using left and right sticks
barometerInterval = 3600 * 2    # Update barometer value array size - two hours so we can compare old to new values
barometerTolerance = 0.01       # parameter for tuning the sensitivity of the barometer LED
fastBarometerTolerance = 0.02   # parameter for showing faster flash if barometer is rising or falling rapidly
fastBlink = False               # fast blink for rapidly changing barometer
#End of parameters
#***********************************************************************************************************


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

def fastBlinkSecond(clockDisplay, dotColor): #do one rapid blink during the on cycle of the second hand to show rapid change in barometer
                                             #clock array is always passed here with the seconds dot lit
    sleep(0.40)                              #let it shine for a while
    clockDisplay[0] = empty                  #turn it off
    sense.set_pixels(clockImage)
    sleep(0.20)
    clockDisplay[0] = dotColor               #restore the original color
    sense.set_pixels(clockImage)
    sleep(0.40)                              #complete the one second dot cycle
    return

#Sleep loop. This operation is complicated by the fact that neither the Python sleep() function nor the SenseHat wait_for_events() function are interruptible, so
#designing a routine that allows two different ways to interrupt the dormant stage (time and button press) is a little involved. This works, though.
#The clock is dark while executing this function.
def holdClock(orientation):           #routine to turn off clock on middle button press, then turn it back on when pressed again
    clockOff = True                                     #Flag to deal with long presses
    sense.clear()                                      #Turn off the clock
    sense.stick.get_events()                           #Clear all old inputs
    while clockOff:                                     #Lets us loop till the explicit set of conditions is satisfied
        sleep (0.25)                                   #Four times a second ought to be enough. Reduce CPU load.
        turnClockOn = sense.stick.get_events()          #Would normally use wait_for_event to sleep till the button is pressed again, but need to wake up now and then to check time
        if ((len(turnClockOn) > 0) | (not(clockAlwaysActive))):     #If there may be a timed wakeup, check status whether or not the button was pressed
            passedTest = False                                  #Workaround for Python limitation - all conditions checked in compound if, even if the first is invalid and causes errors in the rest
            if (len(turnClockOn) > 0):                           #First test: is this a button press?
                if ((turnClockOn[len(turnClockOn) - 1].direction == "middle") & (turnClockOn[len(turnClockOn) - 1].action == "released")):    #If we want timed on/off, check for button and time
                    passedTest = True
                else:
                    orientation = lightLevel(turnClockOn, orientation)                      #Are we trying to dim or brighten the clock?
            else:
                if ((not(clockAlwaysActive)) & (time.localtime().tm_hour == activeTimeStartHour) & (time.localtime().tm_min == activeTimeStartMinute) & (time.localtime().tm_sec < 3)):    #We only test for time if the button test failed. 
                    passedTest = True
                else:
                    pass
            if passedTest == True:
                clockOff = False
                sense.stick.get_events()                       #Clear the event queue so the clock doesn't turn right off again
            else:
                pass                                           #The clock is still supposed to be off - keep going.
        else:
            pass

def lightLevel(turnClockOn, orientation):     #Added orientation as parameter
    #Note that the clock is meant to be run with the Pi inverted, so up is literally down. That explains the reversed logic in this method.
        if ((turnClockOn[len(turnClockOn) - 1].direction == "up") & (turnClockOn[len(turnClockOn) - 1].action == "released")):      #Up and down are switches for full light and low light
            sense.low_light = True                                                                                                #Dim display (up is actually down)
        elif ((turnClockOn[len(turnClockOn) - 1].direction == "down") & (turnClockOn[len(turnClockOn) - 1].action == "released")):     
            sense.low_light = False                                                                                               #Bright display (down is actually up)
        elif ((turnClockOn[len(turnClockOn) - 1].direction == "right") & (turnClockOn[len(turnClockOn) - 1].action == "released")):
            orientation = orientation + 90          #rotate clockwise
            if (orientation >= 360):
                orientation = orientation - 360     #bring angle back into reasonable range
        elif ((turnClockOn[len(turnClockOn) - 1].direction == "left") & (turnClockOn[len(turnClockOn) - 1].action == "released")):
            orientation = orientation - 90          #rotate counterclockwise
            if (orientation < 0):
                orientation = orientation + 360     #bring angle back to usable range
        else:
            pass
        return orientation
    
def avgPressure(baromArr, phase):            #Get the average pressure for the five minutes at the start or end of the time period. Avoids frequent changes in top dot color.
    period = 300              #number of entries to be averaged, in seconds
    avg = 0
    if (phase == 'first'):
        start = 0
    elif (phase == 'last'):
        start = len(baromArr) - period
    else:
        start = 0                             #this shouldn't happen, so just return an arbitrary value
    for i in range (start, start + period):
        avg = avg + baromArr[i]
    avg = avg / period                            #We could return the total instead of the average, but this would be easier to debug if needed
    avg = int(avg * 1000) / 1000.               #Round to three decimal places so we can do the math later
    return avg
        
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


barometerTimer = 0      #Initialize counter
currentPressure = int(mToi(sense.get_pressure()) * 100) / 100.

pressureArray = []                                              #Define array for barometric pressure - will be a sliding window that updates every minute
pressureArray = initBarometer(pressureArray, barometerInterval) #Start with the same value every minute. Eventually we'll be able to look back once a minute to the value a barometerInterval ago.
#print (pressureArray, len(pressureArray))

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
        print ('12 hour mode')
else:
        print ('24 hour mode')
if blinkingSecond:
        print ('Blinking seconds enabled')
        if blinkingBarometer:
                print ('Barometer color enabled')
        else:
                print ('Barometer color disabled')
else:
        print ('Blinking seconds disabled')
                

while True:
    #Optional setting for dimming display at night
    if dimDisplay:
        if (time.localtime().tm_hour == dimDisplayHour) & (time.localtime().tm_min == 0) & (time.localtime().tm_sec < 3):
            sense.low_light = True      #dim display
        if (time.localtime().tm_hour == brightDisplayHour) & (time.localtime().tm_min == 0) & (time.localtime().tm_sec < 3):
            sense.low_light = False      #bright display
    if (clockAlwaysActive == False) & (time.localtime().tm_hour == quietTimeStartHour) & (time.localtime().tm_min == quietTimeStartMinute) & (time.localtime().tm_sec < 2):  #Time to go to sleep? 
                                                                                                                                                                             # Seconds reading needed so we don't turn the clock off again after manually turning it on.
        holdClock(orientation)         #Check first for the timer - are we sleeping the clock?
    switchOff = sense.stick.get_events()     #Has the button been pressed to turn the clock off?
    if len(switchOff) > 0:
        if (switchOff[len(switchOff) - 1].direction == "middle") & (switchOff[len(switchOff) - 1].action == "released"):    #Was the middle button pressed?
            holdClock(orientation)
        else:
            orientation = lightLevel(switchOff, orientation)              #Are we trying to dim or brighten the clock?
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

    sense.set_rotation(orientation) # Optional
#    sense.low_light = True # Optional
    if blinkingSecond:
        if blinkingBarometer:
#                barometerTimer = barometerTimer + 1
#                if barometerTimer >= barometerInterval:      #get ready to update the barometer dot color
#                        barometerTimer = 0                   #reinitialize
#                        oldPressure = currentPressure
            currentPressure = int(mToi(sense.get_pressure()) * 100) / 100.   #make sure the change is significant - two decimal places
            pressureArray = shiftPressures(pressureArray, currentPressure)                  #put the new pressure at the end of the array
            oldPressure = pressureArray[0]                                  #look back as far as possible
#                print (oldPressure, currentPressure, pressureArray)
#                currentPressure = currentPressure * (random() + 0.5)
#                print (oldPressure, currentPressure)
            oldAvg = avgPressure(pressureArray, 'first')
            currAvg = avgPressure(pressureArray, 'last')
#        print (oldPressure, currentPressure, oldAvg, currAvg)
            if oldAvg - currAvg > barometerTolerance:
                dotColor = red          #pressure falling
            elif oldAvg - currAvg < barometerTolerance * -1.0:
                dotColor = green        #Pressure rising
            else:
                dotColor = white        #Pressure steady (within margin of error)
        else:
            dotColor = white            #We're not tracking the barometer, default seconds color is white

#Update - add fast blink if barometer is changing rapidly
        if blinkingBarometer:
            if (abs(oldAvg - currAvg) >= fastBarometerTolerance):   #Did barometer just start rising or falling rapidly?
                fastBlink = True                                    #Double the treetop blink rate
            elif (abs(oldAvg - currAvg) < fastBarometerTolerance):  #Did barometer just stop rising or falling rapidly?
                fastBlink = False                                   #Reset to default blink rate
            else:
                pass          #Nothing changes
#            print (oldAvg, currAvg, abs(oldAvg - currAvg))
        else:
            pass
               


#        if oldPressure > currentPressure:
#            dotColor = red          #pressure falling
#        elif oldPressure < currentPressure:
#            dotColor = green        #Pressure rising
#        else:
#            dotColor = white        #Pressure steady (within margin of error)
        clockImage[0] = dotColor
        sense.set_pixels(clockImage)
        if fastBlink:
            fastBlinkSecond(clockImage, dotColor)        #Flash the seconds icon to show rapid rise
        else:
            sleep(1)
        clockImage[0] = empty
        sense.set_pixels(clockImage)
        sleep(1)
    else:
        sense.set_pixels(clockImage)
        sleep(2)
        
