#!/bin/bash

# Definitions
usb_dir=/media/usb
working_dir=~/working-directory


device=$(sudo fdisk -l | grep -o '^/dev/sd[a-z][0-9]') # identify /dev/sda1 or so as the USB device
echo -e "Device: ${device} \n"

echo -e "Mount USB device"
sudo rm -r ${usb_dir}
sudo mkdir ${usb_dir} # prepare mounting directory
sudo chmod 777 ${usb_dir} # assign full permissions
sudo mount ${device} ${usb_dir} # mount the device to the dedicated folder

echo -e "\n USB device files:"
ls ${usb_dir} # check usb files

echo -e "\n Copy files USB device -> working directory"
sudo rm -r ${working_dir}
sudo mkdir ${working_dir}
sudo cp ${usb_dir}/* ${working_dir}/ # copy present files 

echo -e "\n Copied files USB device -> working directory:"
ls ${working_dir} # check files
