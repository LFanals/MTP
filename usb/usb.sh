device=$(sudo fdisk -l | grep -o '^/dev/sd[a-z][0-9]') # identify /dev/sda1 or so as the USB device
echo -e "Device: ${device} \n"

echo -e "Mount device"
sudo mkdir /media/usb # prepare mounting directory
sudo chmod 777 /media/usb # assign full permissions
sudo mount ${device} /media/usb # mount the device to the dedicated folder

echo -e "\n Device files:"
ls /media/usb # check files

echo -e "\n Copy files"
mkdir ~/working-directory
cp /media/usb/* ~/working-directory/ # copy present files 

echo -e "\n Copied files:"
ls ~/working-directory # check files
