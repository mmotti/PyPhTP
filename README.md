# PyPhTP
Shrink, eject and inject your gravity database for Pi-hole

This script has been created for those of you whom are struggling to teleport / sync your Pi-hole database due to it's excessive size.

### Requirements ###
Python **3.6+**

### What does it do? ###
The script will clear the gravity table and run a Vacuum on your Pi-hole database, before copying it to the output directory (**/etc/pihole/PyPhTP/**). It will then run `pihole -g` to re-populate your gravity table.

### How does this help me? ###
You can take your dumped Pi-hole DB from the output directory, and find a way to sync it with your other Pi-holes.

### How to use ###

There are two main steps to this script:

#### eject ####
Shrink database, copy it to **/etc/pihole/PyPhTP/** and run `pihole -g`

`curl -sSl https://raw.githubusercontent.com/mmotti/PyPhTP/master/PyPhTP.py | sudo python3 - --eject`

#### inject ####
Take the database from **/etc/pihole/PyPhTP/**, overwrite the one in **/etc/pihole** and run `pihole -g`

`curl -sSl https://raw.githubusercontent.com/mmotti/PyPhTP/master/PyPhTP.py | sudo python3 - --inject`
