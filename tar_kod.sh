#!/bin/sh
#Created by Mike Lee 2020-01-06
#Driver program

#Prompts user for folder name
read -p "Enter the name of your output folder: " NAME

#Checks to see if this folder does exist
if [ ! -d "$NAME" ]; then
    read -p "The $NAME directory does not exist."
    exit 1
fi

nohup tar_kod.py $NAME

echo "Tarring files ..."