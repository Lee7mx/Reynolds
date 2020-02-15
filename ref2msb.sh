#!/bin/sh
#Created by Mike Lee 2019-11-15
#Calls the driver program, refl2msb.py. Asks for user inputs that feeds into the refl2msb.py.

LOG="nohup.out"
OUT="outfile.out"

read -p "What store is it? (e.g. 01): " STORE
read -p "What branch is it for? (e.g. 01): " BRANCH
read -p "What company is it for? (This should be where your volume folders are located): " COMPANY

#Checks to see if there is an already existing nohup.out
if [ -f $LOG ]; then
    read -p "There is already a nohup.out, would you like to save a copy? (y/n, n will just overwrite it): " PROMPT1
    if [ $PROMPT1 == 'y' ]; then
        read -p "What would you like to save it as?: " PROMPT2
        mv $LOG ./$PROMPT2
    else
        rm $LOG
    fi
fi

#Checks to see if there is an existing outfile.out
if [ -f $OUT ]; then
    read -p "There is already an outfile.out, would you like to save a copy? (y/n, n will just overwrite it): " PROMPT3
    if [ $PROMPT2 == 'y' ]; then
        read -p "What would you like to save it as?: " PROMPT4
        mv $OUT ./$PROMPT4
    else
        rm $OUT
    fi
fi

#Checks to see if the Company file actually exists, will exit out if there isn't one.
if [ ! -d "$COMPANY" ]; then
    echo "The company subdirectory does not exist. You need to create the subdir company folder that contains the vol folders."
    exit 1
fi

nohup ref2msb.py $STORE $BRANCH $COMPANY &

echo "Documents are processing ..."