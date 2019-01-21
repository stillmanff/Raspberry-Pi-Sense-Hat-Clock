Displays the Raspberry Pi's time on a Sense Hat

Each digit is 3x4 pixels so the time is shown as:

H H

M M 

on the Sense Hat

Rich Stillman (stillmanff) adds:

1. Added internal timer loop to make the clock work standalone instead of invoking cron
2. Added a 12 hour mode that can be toggled via the twelvehour boolean
3. Added a blinking LED as a "second hand" that can be toggled via the blinkingSecond boolean
4. Turned off the high order digit in single digit hours

Start with 
```python clock.py & ```

If you don't want terminal output, use
```python clock.py > /dev/null &

Update 11/5/2018:
Changed blinking second pixel to include barometric pressure information.
Clock compares current pressure with pressure from a half hour ago (sliding window).
Displays green if rising, red if falling.
Program measures barometric pressure in in/Hg and rounds to 1/100th inch.

Update 1/21/2019:
Added joystick controls based on christmastree project
1. Center press on joystick turns display on/off
2. Joystick down dims display (sense.low_light = True)
3. Joystick up brightens display

Also, fixed time on/off logic to play nicely with switch display on/off.

Note that the program is written to use the Pi upside down (power cable on top).
Therefore, the up/down logic of the joystick is inverted.

Coming features:
1. Different colors for "rising/falling rapidly" and "rising/falling slowly"
2. Press the joystick to temporarily display current barometric pressure

Note: None of the other PiHat sensors seem accurate enough for real world use.
