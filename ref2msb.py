#!/usr/bin/env python
#Created by Mike Lee 2019-11-15
#Simulates the ARKREFL.MSB

import os, sys, csv, itertools
from shutil import copyfile, rmtree
from datetime import datetime, time
from signal import signal, SIGINT


#Grabs the current date/time
now = datetime.now()
dt = now.strftime("%m/%d/%Y  %H:%M:%S")
#Grabs user input from the shell script
store = sys.argv[1]
branch = sys.argv[2]
company = sys.argv[3]
cwd = os.getcwd() #Get the current working directory
global fl #File length of the INDEX file
fl = 0
doccount = 0
totalcount = 0
misscount = 0
global arkcount
global arkvol
arkcount = ''
arkvol = ''

####################USER DEFINED METHODS####################

#Method to handle exiting the program
def handler(signal_received, frame):
    #Handle a force quit using ctrl c
    print(' detected, exiting program.')
    exit(0)

#Method to format date strings
def format_date(str):
    split = str.split('/')
    date = split[0]+'-'+split[1]+'-20'+split[2]
    return date

#There are certain fields, where customer names are formatted "LAST, FIRST". This will try and correct it
def check_name(str):
    name = str
    if ',' in str:
        split = name.split(',')
        name = split[1][1:] + ' ' + split[0]
    return name

#Increment the number of documents in the current volume
def increment_vol():
    global doccount
    doccount += 1

#Resets the count of volume
def reset_vol():
    global doccount
    doccount -= doccount

#Increment the total number of documents written to the outfile
def increment_total():
    global totalcount
    global doccount
    totalcount += doccount

#Increment the number of documents with missing doctypes/docdates
def increment_miss():
    global misscount
    misscount += 1

#Sets the arkcount based on passed value
def set_arkcount(count):
    global arkcount
    arkcount = count

#Sets the arkvol based on passed value
def set_arkvol(vol):
    global arkvol
    arkvol = vol

#Method that will process the lines passed in from the read_file method
#Using various cases to build the document based on certain fields
def process_doc(lines,index):
    try:
        #Creating a temporary array to build a single document/row in the all.msb
        tempdoc = []
        arkarray = []
        #Initializing variables
        title = ''
        application = ''
        subtitle = ''
        doctype = ''
        ro = ''
        inv = ''
        deal = ''
        check = ''
        cust = ''
        name = ''
        deposit = ''
        vin = ''
        receipt = ''
        po = ''
        docdate = ''
        fullpath = ''
        source = ''
        doccount = 0

        for line in lines:
            #Cleans the raw data before processing.
            line = line.replace('\r','')
            line = line.replace('\n','')
            #Uncomment the line below for testing purposes
            #print line
            #Looking for the title, html format uses "<a href=" for titles.
            #The subtitle is on the same line as the title, so it is slicing a different section of the line.
            if len(line)>1 and '<a href=' in line:
                templine = line.split('<a href=')
                temp1 = templine[1].split(' target')
                temp2 = templine[1].split('=_new>')
                temp2 = temp2[1].split('</a>&nbsp')
                title = temp1[0]
                subtitle = temp2[0]
                arkarray.append(subtitle)
            elif len(line)>1 and 'nbsp' in line:
                line = line.split('font size="1">')
                line = line[1].split('&nbsp')
                line = line[0]
                arkarray.append(line)
            elif line == '<tr>': arkarray.append(line)
            elif line == '</tr>':.
                arkarray.append(line)
                with open(cwd + '/outfile.out','a') as fout:
                    #At the end of the file there are 2 lines, one indicates the number of docs in vol, the other indicates vol num
                    #This is just another check in place to make sure everything is good
                    if len(arkarray) == 2:
                        arkarray.pop()
                        if 'documents processed for this disk' in arkarray[0]:
                            split = arkarray[0].split(' documents processed for this disk.')
                            set_arkcount(split[0].strip("0"))
                            break
                        elif 'VOLUMEID' in arkarray[0]:
                            set_arkvol(arkarray[0])
                            break
                    #Removing '<tr> and </tr> from the array
                    arkarray = arkarray[1:-1]
                    #Uncomment the line below for testing purposes
                    #print line
                    #Setting the static fields
                    fullpath = index.replace('INDEX.HTM',title)
                    source = arkarray[36]
                    datearray = arkarray[1].split('-')
                    docdate = datearray[1]+'-'+datearray[2]+'-'+datearray[0]
                    #Setting the branch field based on the folder1 key from the INDEX.HTM
                    if arkarray[6] == 'ACCOUNTING': application = 'Acctg'
                    elif arkarray[6] == 'PARTS': application = 'Parts'
                    elif arkarray[6] == 'SERVICE': application = 'Servc'
                    elif arkarray[6] == 'CARDEALS': application = 'Fandi'
                    application = application + str(branch)
                    #Uncomment the line below for testing purposes
                    #print arkarray
                    #Setting the variables based on keys in the INDEX.HTM file. Edit if missing or if changes are needed.
                    if arkarray[2] == 'CASHRECEIPTS' or arkarray[0] == 'Cash Receipt':
                        doctype = 'CASHRCPT'
                        receipt = arkarray[12]
                        name = arkarray[15]
                    elif 'CHECK' in arkarray[2] or arkarray[0] == 'A/P Check Accounting' or arkarray[0] == 'A/P Check Accounting Copy':
                        doctype = 'APCK'
                        name = check_name(arkarray[16])
                        check = arkarray[12]
                    elif 'DEPOSIT' in arkarray[2] or arkarray[0] == 'Deposit Slip':
                        doctype = 'DEPOSIT'
                        name = check_name(arkarray[12])
                        if 'N.A.' in name: name = name.replace('N.A. ','')
                        deposit = arkarray[13]
                    elif 'TRIAL BALANCE' in arkarray[0]: doctype = '0370'
                    elif 'Parts Accounting Invoice' in arkarray[0] or 'Part Invoice' in arkarray[0]:
                        doctype = 'PTINV'
                        inv = arkarray[12]
                        name = check_name(arkarray[13])
                    elif 'RO#' in arkarray[0] or arkarray[2] == 'SD' or arkarray[0] == 'Service Documents':
                        doctype = 'RO'
                        ro = arkarray[12]
                        if '/' in ro:
                            split = ro.split('/')
                            ro = split[0]
                        name = check_name(arkarray[13])
                        vin = arkarray[14]
                    elif 'Car Deals' in arkarray[0]:
                        doctype = 'DEALENV'
                       docdate = arkarray[13]
                        deal = arkarray[12]
                        if '/' in deal:
                            split = deal('/')
                            deal = splti[0]
                        name = check_name(arkarray[18])
                    elif 'PURCHASEORDER' in arkarray[2] or 'Purchase Order' in arkarray[0]:
                        doctype = 'PO'
                        docdate = format_date(arkarray[15])
                        po = arkarray[12]
                        name = check_name(arkarray[13])
                        inv = arkarray[16]
                    #Creating the temporary array that will write out to the outfile
                    tempdoc.extend((store,application,doctype,docdate,name,inv,deal,ro,vin,receipt,check,deposit,po,fullpath,source))
                    #Checks for documents with missing doctypes or docdates, writes them out to another file.
                    if doctype == '' or docdate == '':
                        with open('missing_doc.out','a') as fout2:
                            fout2.write('|'.join(str(key) for key in tempdoc) + '\n')
                            increment_miss()
                    fout.write('|'.join(str(key) for key in tempdoc) + '\n')
                    #doccount += 1
                    #Reset the temporary array
                    tempdoc = []
                    #Increment the number of documents in current volume
                    increment_vol()
                #Reset the array created from INDEX.HTM
                arkarray = []
            else:
                break
        #Increment the total number of documents written to the outfile
        increment_total()

    except ValueError as e:
        print('ERROR: ' + e)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print('ERROR: ',exc_type, fname, exc_tb.tb_lineno,e)
        return

#Method that will calculate the file length
def file_len(file):
    with open(file) as f:
        for i, l in enumerate(f):
            pass
    return i + 1

#Method that will return the next set of lines of metakeys
def read_file(file, fl,index):
    with open(file, 'r') as fin:
        lines = itertools.islice(fin, 45, fl)
        for line in lines:
            process_doc(lines,index)

###############################################################################




def main():

    #Prints output to the nohup.out file
    print 'Reflections to IDM conversion has started at ' + dt
    print 'Currently converting documents ... Please check the nohup.out for updates'
    sys.stdout.flush()

    try:
        #Creating the outfile that will be used for GEN.MSB
        outpath = cwd+'/outfile.out'
        with open(outpath,'w') as fout:
            #Writing out the header for the outfile
            fout.write('STORE|BRANCH|DOCTYPE|DOCDATE|NAME|INV|DEAL|RO|VIN|RECEIPT|CK|DEPOSIT|PO|FULLPATH|SOURCE\n')

        #Creating the missing_doc that will let you know if there are documents with missing doctypes or docdates
        misspath = cwd+'/missing_doc.out'
        with open(misspath,'w') as fout2:
            fout2.write('These documents are either missing doctypes or docdates. Fix before running GEN2MSB.')

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print('ERROR: ',exc_type, fname, exc_tb.tb_lineno,e)
        return
    #Building the company path, if there are multiple companies, will need to run ref2msb.sh multiple times
    companypath = cwd + '/' + company
    #List out the volumes in the company dir
    companydir = os.listdir(companypath)
    #Cehcks through each volume dir
    for vol in companydir:
        #Checking for cases
        if vol.startswith('Vol') or vol.startswith('VOL') or vol.startswith('vol'):
            #Sets the path to the INDEX.HTM file
            index = companypath + '/' + vol + '/INDEX.HTM'
            #Sets the file length
            fl = file_len(index)
            #Gets the time/date
            now = datetime.now()
            pt = now.strftime("%m/%d/%Y  %H:%M:%S")
            print 'Processing ' + index + ' at ' + pt
            sys.stdout.flush()
            #Read in the INDEX.HTM
            read_file(index, fl,index)
            #Prints how many documents there were in each volume
            now = datetime.now()
            nt = now.strftime("%m/%d/%Y  %H:%M:%S")
            print 'There are ' + arkcount + ' documents in ' + arkvol
            print 'There were ' + str(doccount) + ' records in ' + vol + ' that were written to the outfile. Finished at ' + nt
            sys.stdout.flush()
        #Resets the count for the volume when it goes to the next one
        reset_vol()
    #Prints the total number of documents written to the outfile
    print
    print 'Total documents converted: ' + str(totalcount)
    print 'Total documents with missing doctypes/docdates: ' + str(misscount) + '  These can be found in missing_doc.out'
    print 'Run GEN2MSB on ' + cwd + '/outfile'


if __name__=="__main__":
    main()