## HOWTO Install Piyak on a Raspberry Pi (tested on a series 3)
On your PC (assumes Win10)
Download the RPi boot image for installation on an SD card (mine was 16Gb, 8Gb is probably OK) https://www.raspberrypi.org/downloads/raspbian/

![buster](https://github.com/logicmonkey/piyak/blob/master/images/raspbian_buster.png)

Right-click and unzip the archive to get the boot image:

![diskimage](https://github.com/logicmonkey/piyak/blob/master/images/show_boot_image.png)

Write the image to your SD card - I used Win32 Disk Imager (other programs are linked from raspberrypi.org):

![wrdiskimage](https://github.com/logicmonkey/piyak/blob/master/images/wr_boot_image.png)

You're done with your PC, the rest is on the RPi itself.

* Connect keyboard, mouse, display to your RPi.
* Insert the newly created SD card.
* Power up and follow the instructions. Set your default user ('pi') password (I stick with 'raspberry'). Connect to your WiFi.
* I LAZILY CHOSE TO SKIP THE SYTEM UPDATE STEP.
* Reboot.

Open a command line terminal and enter the commands:
```
sudo apt-get install python3-sdl2
python3 -m pip install matplotlib
python3 -m pip install kivy==1.11.1
```
Now download the piyak software.
Open the web browser and go to https://github.com/logicmonkey/piyak
Click the "Clone or download" button and download "piyak-master.zip".
Click on the up arrow ^ of the downloaded file at the bottom of the web browser window and "Show in window". Right click and "extract to..." the user `pi` home directory `/home/pi`.
Click "Extract".
You should now have a `piyak-master` directory in `/home/pi` and this contains the piyak files.
Back to the command line terminal window.
Start the GPIO daemon - YOU MUST ALWAYS DO THIS
```
sudo pigpiod
cd piyak-master
```
Run the demo with the command:
```
./piyak-demo.py
```
After a short delay while the system configures itself for the first time, the app should start.
Run the real app with:
```
./piyak.py
```
