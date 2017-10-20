# Set the PWR LED to GPIO mode (set 'off' by default).
echo gpio | sudo tee /sys/class/leds/led1/trigger

# (Optional) Turn on (1) or off (0) the PWR LED.
echo 1 | sudo tee /sys/class/leds/led1/brightness
echo 0 | sudo tee /sys/class/leds/led1/brightness

# Revert the PWR LED back to 'under-voltage detect' mode.
#echo input | sudo tee /sys/class/leds/led1/trigger

# Set the ACT LED to trigger on cpu0 instead of mmc0 (SD card access).
#echo cpu0 | sudo tee /sys/class/leds/led0/trigger
