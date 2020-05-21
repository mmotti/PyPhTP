# PyPhTP
Shrink, eject and inject your gravity database for Pi-hole

This script has been created for those of you whom are struggling to teleport / sync your Pi-hole database due to it's excessive size.

### Requirements ###
Python **3.6+**

### What does it do? ###
The script will clear the gravity table and run a Vacuum on your Pi-hole database, before copying it to the output directory (**/etc/pihole/PyPhTP/**). It will then run `pihole -g` to re-populate your source gravity table.

You can also use this script to inject a previously ejected database; so if you sync the output directory on your primary Pi-hole with a secondary Pi-hole, then run this script in inject mode on the secondary, it can keep your database in sync.

### How to use ###

There are two main steps to this script:

#### eject ####
Shrink database, copy it to **/etc/pihole/PyPhTP/** and run `pihole -g`

`curl -sSl https://raw.githubusercontent.com/mmotti/PyPhTP/master/PyPhTP.py | sudo python3 - --eject`

#### inject ####
Take the database from **/etc/pihole/PyPhTP/**, overwrite the one in **/etc/pihole** and run `pihole -g`

`curl -sSl https://raw.githubusercontent.com/mmotti/PyPhTP/master/PyPhTP.py | sudo python3 - --inject`
