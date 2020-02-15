#!/bin/sh
#Created by Mike Lee 2020-01-07
#Driver for kod2msb.py

LOG="nohup.out"
OUT="outfile.out"
DV="DV"
#Checks to see if there is already existing nohup.out, if there is it will ask the user if it wants to save the copy of it.
if [ -f $LOG ]; then
    read -p "There is already a nohup.out, would you like to save it? (y/n, n will overwrite it): " PROMPT1
    if [ $PROMPT1 == 'y' ]; then
        read -p "What would you like to save it as?: " PROMPT2
        mv $LOG ./$PROMPT2
    else
        rm $LOG
    fi
fi

#Checks to see if there is an existing DV folder, will ask user if they would like to overwrite it
if [ -d $DV ]; then
    read -p "There is already a DV folder, would you like to save it? (y/n, n will overwrite it): " PROMPT3
    if [ $PROMPT3 == 'y' ]; then
        read -p "What would you like to save it as?: " PROMPT4
        mv $DV ./$PROMPT4
    else
        rm -r DV
        mkdir -m 777 'DV'
        mkdir -p DV/Conv{1..10}
        chmod 777 DV/Conv*
    fi
else
    mkdir -m 777 'DV'
    mkdir -p DV/Conv{1..10}
fi

#Checks to see if a sched.map file exists, if not, it will prompt the user to create one.
if [ ! -f "sched.map" ]; then
    echo "The sched.map file is missing, please create one using the data from the customer's ERA server."
    exit 1
fi

#Checks to see if the Summary.txt file exists.
if [ ! -f "Summary.txt" ]; then
    echo "The Summary.txt file is missing, this file is provided by Kodata and helps validate the conversion."
    exit 1
fi

#Checks to see if an outfile already exists, if not it will prompt the user if they would like to delete it.
if [ -f $OUT ]; then
    read -p "An outfile already exists, would you like to save it? (y/n, n will overwrite it): " PROMPT5
    if [ $PROMPT3 == 'y' ]; then
        read -p "What would you like to save it as " PROMPT6
        mv $OUT ./$PROMPT4
    fi
fi
#Prompts user for name of folder containing stores/branches
read -p "What is the name of the folder that contains your data? (Not the full path i.e. Sharpe): " PROMPT7

#Calls the python program
nohup kod2msb.py $PROMPT7 &

echo "Documents processing ..."
