Displays the Raspberry Pi's time on a Sense Hat

Each digit is 3x4 pixels so the time is shown as:

H H

M M 

on the Sense Hat

I've set it up in crontab to run every minute.

```sudo crontab -e```

Add the following to run it every minute:

```* * * * * /home/pi/clock/clock.py >/dev/null 2>&1```

This assumes the python program is in directory ```/home/pi/clock/```

Rich Stillman (stillmanff) adds:

1. Added internal timer loop to make the clock work standalone instead of invoking cron
2. Added a 12 hour mode that can be toggled via the twelvehour boolean
3. Added a blinking LED as a "second hand" that can be toggled via the blinkingSecond boolean
4. Turned off the high order digit in single digit hours

Start with 
```python clock.py & ```

If you don't want terminal output, use
```python clock.py > /dev/null &
