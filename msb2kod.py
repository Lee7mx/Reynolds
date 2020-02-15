#!/usr/bin/env python
#Created by Mike Lee 2019-09-09
#Last Modified on 11/11/19
#Emulating the MSB2KODATA script into python. Trying to clean up the process as Kodata is creating a new process on their side.

import os, sys, csv
from shutil import copyfile, rmtree
from datetime import datetime, time
from itertools import groupby
from signal import signal, SIGINT


#Grabs the current date/time.
now = datetime.now()
dt = now.strftime("%m/%d/%Y  %H:%M:%S")
doctypes = []
counts = []



##########################################USER DEFINED METHODS############################################

#Method to count the number of lines of all files in ./DV/ConvDept/*
def line_count(fn):
    os.chdir('./DV/ConvDept')
    with open(fn) as f:
        for i, l in enumerate(f):
            pass
    return i + 1

#Method to check for file name length as well as special characters in a given field
def clean_field(field):
    specialChars = ['@','#','$','%','*','(',')','=','+','[',']','{','}','"','/']
    newField = ''
    for each in field:
        for char in specialChars:
            if char == each:
                newField = field.replace(field[field.index(char)], '_')
        if newField == '':
            newField = field
    newField = newField.replace("\r","").replace("\n","")
    if len(newField) < 100:
        return newField
    else:
        newField = newField[99:]
        return newField

#Method to remove duplicate consecutive characters. Takes in a string and character.
def remove_dupes(s, c):
    return ''.join(c if a==c else ''.join(b) for a,b in groupby(s))

#Method to handle exiting the program.
def handler(signal_received, frame):
    #Handle a force quit using ctrl c
    print(' detected, exiting program.')
    exit(0)

#Method that will count the number of documents for each doctype for validation purposes.
def check_doctype(dt):
    global doctypes
    global counts

    if not dt in doctypes:
        doctypes.append(dt)
        counts.append(1)
    else:
        for x in doctypes:
            if x == dt:
                index = doctypes.index(x)
                counts[index] = counts[index] + 1

#Method that will print out the number of doctypes
def print_doctypes():
    global doctypes
    global counts

    #for (index, element) in enumerate(doctypes):
        #print(element + ': ' + str(counts[index])
    fmt = '{0:<20}{1}'
    print(fmt.format('Doctype', 'Count'))
    print('------------------------------')
    for i, (dt,ct) in enumerate(zip(doctypes, counts)):
        print(fmt.format(dt, ct))
###########################################################################################################



def main():
    #Declaration/Initialization of variables
    ###########################################################################################################
    global doccount
    global count
    count = 1
    doccount = 0
    global cwd
    global docpath
    global newName
    templist = []
    docdirs = []
    dealdocdirs = []
    head = []
    output = sys.argv[1]
    delete = sys.argv[2]
############################################################################################################

    try:
        #Calls handling method for ctrl c
        signal(SIGINT, handler)
        #Stores current working directory
        cwd = os.getcwd()
        #Checks to see if there is a DV folder as well as a ConvDept folder, regardless of case.
        if os.path.exists(cwd + '/DV/ConvDept'):
            dv = os.listdir(cwd + '/DV/ConvDept')
            dvPath = cwd + '/DV/ConvDept'
        elif os.path.exists(cwd + '/DV/convdept'):
            dv = os.listdir(cwd + '/DV/convdept')
            dvPath = cwd + '/DV/convdept'
        #If the path doesn't exist, prompts the user to check to see if there was a DV/ConvDept folder
        else:
            print "ABORTING CONVERSION ... Check the DV/ConvDept folder."
            return
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print('ERROR: ',exc_type, fname, exc_tb.tb_lineno,e)
        return
    except KeyboardInterrupt as e:
        raise
#############################################################################################################



#This block is creating the output folder. This is where all of the documents will be stored.               #
#############################################################################################################
    try:
        #Checks to see that the output folder doesn't already exist. If so, create it.
        if delete.lower() == 'y':
            rmtree(cwd + '/' + output)
            print "Deleting " + output + " folder ...\n\n"
        else:
            if not os.path.exists(cwd+'/'+output):
                os.makedirs(cwd+'/'+output)
                os.chmod(cwd+'/'+output,0o777)
            else:
                print output + ' folder already exists, answer prompt y to delete folder or manually remove it yourself.\n\n'
                return
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print('ERROR: ',exc_type, fname, exc_tb.tb_lineno,e)
        return
    except KeyboardInterrupt as e:
        raise
#############################################################################################################



#Lets user know the conversion has started.
#############################################################################################################
    print 'IDM to Kodata conversion has started at ' + dt
    print 'Currently converting documents ...\n\n'
    #This flushes out any output that hasn't already printed.
    sys.stdout.flush()
#############################################################################################################



#Stores the header and declares the values for each variable.
#############################################################################################################
    try:
        #Parses the msb file/s.
        for msbfile in dv:
            #Checks for msb files only
            if msbfile.endswith('.msb'):
                msbpath = dvPath + '/' + msbfile
                #Opens the msb file
                with open(msbpath, 'r') as fin:
                    reader = csv.reader(fin, delimiter=',')
                    now = datetime.now()
                    pt = now.strftime("%m/%d/%Y  %H:%M:%S")
                    print "Processing " + msbfile + " at " + pt + '\n\n'
                    #Skips the first five lines as they don't really mean anything.
                    for i in range(6):
                        next(reader)
##############################################################################################################################



#Sets variables that aren't pulled directly from the msb file such as day, year, application, etc.
##############################################################################################################################
                    #Parses each line
                    for row in reader:
                        journal = clean_field(row[10])
                        stock = clean_field(row[11])
                        receipt = clean_field(row[12])
                        branch = row[13]
                        name = clean_field(row[14])
                        deal = clean_field(row[15])
                        ro = clean_field(row[16])
                        doctype = clean_field(row[17])
                        sched = clean_field(row[18])
                        cust = clean_field(row[19])
                        inv = clean_field(row[20])
                        ven = clean_field(row[21])
                        ck = clean_field(row[22])
                        store = row[23]
                        docdate = row[24]
                        vin = clean_field(row[25])
                        po = clean_field(row[26])
                        #Sets up date attributes based on the date field for each document
                        date = datetime.strptime(str(docdate), '%m-%d-%Y')
                        month =  date.strftime('%B')
                        year =  date.year
                        day = date.day
                        #Creates strings from the fields in order to create the directory folder names
                        dateStr = str(month) + '-' + str(day) + '-' + str(year)
                        branchStr = 'Branch' + branch[-2:]
                        check_doctype(doctype)
##############################################################################################################################



#Creating the folder structure.
#Customers often need to look up deals. They don't typically know the deal number, so they have requested
#to make folders for deals by customer names/vins/customer numbers.
##############################################################################################################################
                        #Checks to see if it is a doctype of 'DEALENV' or 'DPWDOCS'
                        if (str(doctype) == 'DEALENV') or (str(doctype) == 'DPWDOCS'):
                            if name == '':
                                name = 'UnknownID'
                            #Adds the values into an array.
                            dealdocdirs.append((store.zfill(1),branch.lower(),doctype,name.replace(' ','_')+'~'+vin,year,month))
                            #Using the previous array, we are creating a 2D array
                            for x in range(len(dealdocdirs)):
                                templist = []
                                for y in range(len(dealdocdirs[x])):
                                    templist.append(dealdocdirs[x][y])
                                #The new directory structure is created using the 2D array
                                newDir = cwd + '/' + output + '/' + 'Store' + str(templist[0]) + '/' + branchStr + '/' + str(templist[1]) + '/' + str(templist[2]) + '/' + str(templist[3]) + '/' + str(templist[4]) + '/' + str(templist[5])
                                #If the directory structure doesn't exist, create it. Otherwise, pass.
                                if not os.path.exists(newDir):
                                    os.makedirs(newDir)
                                else:
                                    pass
                        #Same thing as above, but for the rest of the doctypes
                        else:
                            #Fills in a 2D Array that contains the application, doctype, year and month
                            docdirs.append((store.zfill(1),branch.lower(),doctype,year,month))
                            for x in range(len(docdirs)):
                                #Resets a temporary list
                                templist = []
                                for y in range(len(docdirs[x])):
                                    templist.append(docdirs[x][y])
                                #Using the templist, new directory structure is created
                                newDir = cwd + '/' + output + '/' + 'Store' + str(templist[0]) + '/' + branchStr + '/' + str(templist[1]) + '/' + str(templist[2]) + '/' + str(templist[3]) + '/' + str(templist[4])
                                #Creates the new directory
                                if not os.path.exists(newDir):
                                    os.makedirs(newDir)
##############################################################################################################################



#Gets the file extension as well as the full path to the file in the DV folder
##############################################################################################################################
                        ext = ''
                        path = ''
                        for element in row:
                            if "<BASE>" in element:
                                ext = element[-4:]
                                path = element[6:]
                                path = path.replace('\\','/')
##############################################################################################################################



#Using the clean fields, constructing a new name for the file
##############################################################################################################################
                        newFileName = ''
                        countStr = str(count).zfill(6)
                        newFileName = ck + '~' + deal + '~' + ro + '~' + cust + '~' + ven + '~' + name.replace(' ','_') + '~' + journal + '~' + sched + '~' + vin + '~' + inv + '~' + dateStr + '~' + countStr + ext
                        #Cleaning up the file name
                        nameList = list(newFileName)
                        #Removes any '~' from the beginning of any names
                        while nameList[0] == '~':
                            del nameList[0]
                        newFileName = ''.join(nameList)
                        newFileName = remove_dupes(newFileName,'~')
##############################################################################################################################



#Constructing the new path.
##############################################################################################################################
                        count += 1
                        path = cwd + path
                        if str(doctype) == 'DEALENV' or str(doctype) == 'DPWDOCS':
                            newPath = cwd + '/' + output + '/' + 'Store' + str(store) + '/' + branchStr + '/' + str(branch).lower() + '/' + str(doctype) + '/' + name.replace(' ','_') + '~' + vin + '/' + str(year) + '/' + str(month) + '/' + newFileName
                        else:
                            newPath = cwd + '/' + output + '/' + 'Store' + str(store) + '/' + branchStr + '/' + str(branch).lower() + '/' + str(doctype) + '/' + str(year) + '/' + str(month) + '/' + newFileName
                        #Looks in the old path and copies the file into the new path with the correct file name
                        #Will check if there actually is a document in the old path
                        if os.path.exists(path):
                            try:
                                #Copy the document in the old path into the new directory with the new name
                                copyfile(path,newPath)
                                doccount += 1
                                sys.stdout.flush()
                            #Raise exception if there is an unexpected error
                            except Exception:
                                print 'Error'
                                print path
                                print newPath
                                sys.exc_clear()
                        #If the old path doesn't exist then print the error and continue
                        else:
                            print path + ' not found'
                            continue
##############################################################################################################################



#Raise exceptions
##############################################################################################################################
    except (KeyboardInterrupt, SystemExit):
        raise
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno,e)
    #If there are no exceptions, print success message to user
    else:
        now = datetime.now()
        ft = now.strftime("%m/%d/%Y  %H:%M:%S")
        print 'Conversion has been completed at ' + ft
        #Prints the total doc count
        print "Total Number of Documents Converted: " + str(doccount) + '\n\n'
        print_doctypes()
##############################################################################################################################



if __name__=="__main__":
    main()
