!/bin/sh
#Created by Mike Lee 2019-12-30
#Driver program for msb2kod.py

LOG="nohup.out"
FILE1="$PWD/DV/ConvDept/all.msb"
FILE2="$PWD/DV/convdept/all.msb"

#Check to see if there is a nohup.out, if there is, delete it.
if [ -f $LOG ]; then
    read -p "There is already a nohup.out, would you like to save it? (y/n, n will overwrite it): " PROMPT1
    if [ $PROMPT1 == 'y' ]; then
        read -p "What would you like to save it as?: " PROMPT2
        mv $LOG ./$PROMPT2
    else
        rm $LOG
    fi
fi

#Checks to see if there is a DV folder with an all.msb. Will exit out if there isn't one.
if test -f "$FILE1" -a "$FILE2"; then
    echo "The /DV/convdept/all.msb does not exist."
    exit 1
fi

#Prompts user for folder name
read -p "What would you like to name your output folder?: " NAME

#Checks if there is already one existing, if it is it'll ask if you want to delete it.
if [ -d "$NAME" ]; then
    read -p "This directory already exists, would you like to delete it?(Y/N): " DELETE
else
    DELETE="N"
fi

#Calls python script using 2 user inputs
nohup msb2kod.py $NAME $DELETE &

echo "Documents are processing ..."