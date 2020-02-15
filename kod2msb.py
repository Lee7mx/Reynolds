!/usr/bin/env python
#Created by Mike Lee 2020-01-07
# Emulating the KODATA.MSB, called from the driver, kod2msb.sh.
#
# Will be called from parent directory. Parent directory will contain store directories, that will contain year directories with the associated .DAT files.
#
# EX.)    /mnt/_external_E/Falcone/Parent/Store01/2017
#         |                       |       |       |
#         |                 Parent|Store01|2017   |2017.DAT
#         |                    VOC|Store02|2018   |Doctype Folders
#         |            Summary.txt|Store03|2019   |
#         |              sched.map|       |       |
#
# Run kod2msb.sh and it will run for all stores/branches/years and will create a DV folder in the parent directory with an all.msb file containing all of the keys.

import os, sys, csv
from datetime import datetime, time
from shutil import copyfile

####################GLOBAL VARIABLES########################
start = datetime.now()
st = start.strftime("%m/%d/%Y   %H:%M:%S")
cwd = os.getcwd()
parent_dir = sys.argv[1]
doccount = 0
v_list = []
counts = []

####################USER DEFINED METHODS####################
#Gets the sched num using the sched.map file
def get_schedNum(sched):
    try:
        #Opens sched.map
        with open(cwd+'/'+'sched.map','r') as fin:
            reader = csv.reader(fin)
            for row in reader:
                #Splitting the pipe-delimited file
                split_row = row[0].split('|')
                #Looks to see if the supplied sched num is in the left column, if it is, it will return the number on the right column
                if split_row[0] == sched:
                    return split_row[1]

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print('ERROR: ',exc_type, fname, exc_tb.tb_lineno,e)
        return

#Gets the journal doctype given the journal number
def get_journalType(jrn):
    try:
        jrn = jrn.lstrip('0')
        jrn = int(jrn)
        #These were taken from the KODATA.MSB program.
        if (jrn >= 1 and jrn <= 4) or (jrn == 10) or (jrn == 14):
            doctype = 'SLSJRN'
        elif (jrn >= 11 and jrn <= 13) or (jrn >=16 and jrn <= 17) or (jrn == 30):
            doctype = 'ADJJRN'
        elif (jrn >= 35 and jrn <= 37):
            doctype = 'FAJRN'
        else:
            doctype = 'OTHJRN'
        return doctype

    except Exception as e:
        exc_type,exc_obj,exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print('ERROR: ',exc_type,fname,exc_tb.tb_lineno,e)
        return

#Gets the executable using the document. This number is typically found in the top right corner of a document. Sometimes they don't have one, but it usually helps indicate what doctype the document needs to be set to. This is also supplemented by a spreadsheet provided by Kodata listing all of the executables along with the document names
def get_executable(source_path):
    try:
        executable = 0
        with open(source_path,'r') as fin:
            reader = csv.reader(fin)
            read = []
            check = ''
            for line in fin:
                #Checks to see if there are empty lines, if so, it will get rid of them
                if line in ['\n', '\r\n']:
                    read = reader.next()
                #If the row contains a value
                elif read:
                    #Gets the last 5 characters from the row and will remove empty spaces on either side.
                    check = read[0][-5:].rstrip(' ').lstrip(' ')
                #Checks to make sure that the string is a number as well as making sure it is 4 characters long
                if check.isdigit() and len(check) == 4:
                    executable = float(check)
                    return check
                else:
                    executable = '0'
        return executable

    except Exception as e:
        exc_type, exc_obj,exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print('ERROR: ',exc_type, fname, exc_tb.tb_lineno,e)
        return


#Increments the doc count
def increment_count():
    global doccount
    doccount += 1

#Method that will be used to validate the conversion.
def check_doctype(dt,year,fyi):
    #These lists are used to validate in the compare_counts method
    global v_list
    global counts
    try:
        #If the year/doctype has not been added yet, then add it
        if not ((year,dt)) in v_list:
            if not fyi == '':
                v_list.append((year,dt))
                counts.append(1)
        #Otherwise, parse the list of the year/doctype and increment the count. This is a 2 dimensional list.
        else:
            for x,y in v_list:
                if ((x,y)) == ((year,dt)):
                    index = v_list.index((x,y))
                    counts[index] = counts[index] + 1

    except Exception as e:
        exc_type,exc_obj,exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print('ERROR: ',exc_type,fname,exc_tb.tb_lineno,e)
        return

#Compares the numbers supplied by Kodata with the conversion doc count.
def compare_counts():
    global v_list
    global counts
    summary_list = []
    summary_counts = []
    kodata_sum = 0
    conversion_sum = 0
    print

    try:
        #Opens the Summary.txt file that was supplied by Kodata
        with open('Summary.txt','r') as fin:
            for row in fin:
                #Checks each line of the txt file and will parse them out
                split_row = row.split(':')
                templist = split_row[0].split('\\')
                #Adds the values needed to a list
                summary_list.append((templist[0],templist[1]))
                row_count = split_row[1].split(' ')
                summary_counts.append(row_count[1])
        #Prints output from the Summary.txt as well as the sum of their counts
        for c in summary_counts:
            kodata_sum = kodata_sum + int(c)
        print "Kodata's Count (Taken from Summary.txt) : " + str(kodata_sum)
        print "**************************************************************"
        for ((x,y)) in summary_list:
            if ((x,y)) in summary_list:
                index = summary_list.index((x,y))
                print x + '/' + y + ' : ' + summary_counts[index]
        for cc in counts:
            conversion_sum = conversion_sum + int(cc)
        print
        print

        #Now prints the output from the conversion as well as the sum of their counts
        print "Conversion's Count : " + str(conversion_sum)
        print "**************************************************************"
        for ((a,b)) in v_list:
            index = v_list.index((a,b))
            print a + '/' + b + ' : ' + str(counts[index])

    except Exception as e:
        exc_type,exc_obj,exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print('ERROR: ',exc_type,fname,exc_tb.tb_lineno,e)
        return


def main():

    print 'Kodata to MSB conversion has started at ' + st + '\n\n'
    print
    print 'Currently converting documents ...'
    sys.stdout.flush()

    try:
        #Create the outfile that will be used for GEN.MSB
        outpath = cwd+'/outfile.out'
        with open(outpath,'w') as fout:
            #Writing out the header for the outfile
            fout.write('STORE|BRANCH|DOCTYPE|DOCDATE|NAME|INV|DEAL|RO|VIN|RECEIPT|CHECK|DEPOSIT|PO|FULLPATH|SOURCE\n')

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print('ERROR: ',exc_type, fname, exc_tb.tb_lineno,e)
        return
    try:
        #Storing the dirs that contain either stores or branches, they should all be within the parent directory.
        store_dir = os.listdir(cwd+'/'+parent_dir)
        for store in store_dir:
            branch_dir = os.listdir(cwd+'/'+parent_dir+'/'+store)
            for branch in branch_dir:
                year_dir = os.listdir(cwd+'/'+parent_dir+'/'+store+'/'+branch)
                for year in year_dir:
                    index_dir = os.listdir(cwd+'/'+parent_dir+'/'+store+'/'+branch+'/'+year)
                    for index in index_dir:
                        if index.lower().endswith('.dat'):
                            index_file = index
                            conv_count = 1
                            with open(cwd+'/'+parent_dir+'/'+store+'/'+branch+'/'+year+'/'+index_file,'r') as fin:
                                reader = csv.reader(fin,delimiter=',')
                                for row in reader:
                                    #Setting attributes for the outfile
                                    fyi_doc = []
                                    fyi_store = ''
                                    fyi_branch = ''
                                    fyi_doctype = ''
                                    fyi_docdate = ''
                                    fyi_name = ''
                                    fyi_inv = ''
                                    fyi_deal = ''
                                    fyi_ro = ''
                                    fyi_vin = ''
                                    fyi_receipt = ''
                                    fyi_check = ''
                                    fyi_deposit = ''
                                    fyi_po = ''
                                    fyi_fullpath = ''
                                    fyi_source = ''
                                    #Storing the note field. This field is typically 4 to 8 strings separated by a space
                                    note = row[1]
                                    #Breaking up the note field by the space delimiter
                                    split_note = note.split(' ')
                                    #Storing the original path to the documents.
                                    source_path = row[8]
                                    #Storing the path that will eventually be written to the outfile. This will be modified to accomodate the new location of the files
                                    fyi_fullpath = source_path.replace('\\','/')
                                    #Splitting the path to ignore the windows path to be modified into the linux path
                                    split_path = fyi_fullpath.split('/')
                                    file_name = split_path[9]
                                    doc_path = '/'
                                    #This is getting rid of the inital path to ignore the windows path, i.e. 'E:/' will be changed to '/mnt/_external_E/'
                                    #This should account for wherever you are running this, so if you move it to the archive drive, it should still work as long as you
                                    #edit the dat file to accomodate the changes.
                                    for x in range(3,10):
                                        doc_path = doc_path + split_path[x] + '/'
                                    doc_path = cwd + doc_path
                                    doc_path = doc_path[:-1]
                                    #Getting the docdate provide from the note field, then formats it to use '/' instead of '_'
                                    fyi_docdate = split_note[-1:][0].replace('_','/')
                                    #Calling the method to attain the executable. This is typically found in the top right corner of the document.
                                    ex = get_executable(doc_path)
                                    #Setting the doctype field, this will be the first word of the document name in the note field
                                    doctype = split_note[1]
                                    #Setting the source field, unless Kodata starts supplying us the source of the document, they will all be defaulted to COLD-KODATA
                                    fyi_source = 'COLD-KODATA'
                                    #Grabbing the digit from the store directory that the document resides in
                                    fyi_store = store.replace('Store','')
                                    #Kodata supplies a field of the following format "FolderName\Month". This is used for verification purposes.
                                    dt = row[-2:-1][0].split('\\')
                                    dt = dt[0]
                                    #Testing this
                                    new_path = cwd+'/DV/Conv'+str(conv_count)+'/'+file_name.replace(file_name[-4:],'txt')
                                    fyi_fullpath = split_path[0]+'\\'+split_path[1]+'\\'+split_path[2]+'\\DV\\Conv'+str(conv_count)+'\\'+file_name.replace(file_name[-4:],'txt')

                                    ################################# CREATE NEW DOCTYPES IN THIS SECTION ############################################
                                    if doctype == 'SCH':
                                        fyi_sched = get_schedNum(split_note[2].lstrip('0'))
                                        fyi_doctype = 'SCHED'+str(fyi_sched)
                                        fyi_branch = 'Acctg01'

                                    elif doctype == 'JRN':
                                        fyi_journal = split_note[2]
                                        fyi_doctype = get_journalType(fyi_journal)
                                        fyi_branch = 'Acctg01'

                                    elif 'TRIAL' in split_note or doctype.startswith('CONSOLIDATED') or ex == '0372':
                                        fyi_doctype = '0372'
                                        fyi_branch = 'Acctg01'

                                    elif doctype == 'GENERAL':
                                        if split_note[2] == 'LEDGER' and split_note[3] == 'REPORT':
                                            fyi_doctype = 'GL-ALL'
                                            fyi_branch = 'Acctg01'

                                    elif doctype == 'GL' or ex == '0367':
                                        fyi_doctype = '0367'
                                        fyi_branch = 'Acctg01'

                                    elif doctype == 'VOIDED':
                                        fyi_doctype = '0495'
                                        fyi_branch = 'Acctg01'

                                    elif doctype == 'CHECKS':
                                        fyi_check = split_note[2]
                                        fyi_branch = 'Acctg01'
                                        fyi_doctype = 'APCK'

                                    elif doctype == 'CHECK':
                                        if split_note[2] == 'REGISTER':
                                            fyi_doctype = '0412'
                                            fyi_branch = 'Acctg01'

                                    elif doctype == 'PRINT':
                                        fyi_doctype = 'CASHRCPT'
                                        fyi_branch = 'Acctg01'

                                    elif doctype == 'SERVICE':
                                        if split_note[2] == 'INV':
                                            fyi_doctype = 'SVCINV'
                                            fyi_inv = split_note[3]
                                            fyi_branch = 'Servc'+store[-2:]

                                    elif doctype == 'PARTS':
                                        if split_note[2] == 'INV':
                                            fyi_doctype = 'PTINV'
                                            fyi_inv = split_note[3]
                                            fyi_branch = 'Parts'+store[-2:]

                                    elif doctype == 'PAYROLL':
                                        if split_note[3] == 'CHECK':
                                            fyi_doctype = '1239'
                                            fyi_branch = 'Payrl01'

                                    elif doctype == 'COUNTERPERSON':
                                        fyi_doctype = '2211'
                                        fyi_branch = 'Parts'+store[-2:]

                                    elif ex == '2213':
                                        fyi_doctype = '2213'
                                        fyi_branch = 'Parts'+store[-2:]

                                    elif ex == '1239':
                                        fyi_doctype = '2213'
                                        fyi_branch = 'Payrl'+store[-2:]


                                    elif ex == '2215':
                                        fyi_doctype = '2215'
                                        fyi_branch = 'Parts'+store[-2:]

                                    elif ex == '2543':
                                        fyi_doctype = '2543'
                                        fyi_branch = 'Acctg01'

                                    elif ex == '0685' or doctype == 'P.O.':
                                        fyi_doctype = '0685'
                                        fyi_branch = 'Acctg01'

                                    elif ex == '0424' or doctype == 'TREND':
                                        fyi_doctype = '0424'
                                        fyi_branch = 'Acctg01'

                                    elif doctype == 'PERFORMANCE':
                                        fyi_doctype = '2218'
                                        fyi_branch = 'Parts'+store[-2:]

                                    elif doctype == 'CROSS-POST':
                                        fyi_doctype = 'GL-ALL'
                                        fyi_branch = 'Acctg01'

                                    ################################################################################################################

                                    #Using the fields supplied earlier, adds the values into a list
                                    fyi_doc.extend([fyi_store,fyi_branch,fyi_doctype,fyi_docdate,fyi_name,fyi_inv,fyi_deal,fyi_ro,fyi_vin,fyi_receipt,fyi_check,fyi_deposit,fyi_po,fyi_fullpath,fyi_source])
                                    #Checks to see if there is a doctype and a docdate
                                    if not fyi_doctype == '' and not fyi_docdate == '':
                                        #If both conditions are true, then write out to the outfile
                                        with open(cwd+'/'+'outfile.out','a') as fout:
                                            fout.write('|'.join(str(key) for key in fyi_doc) + '\n')
                                            increment_count()
                                            check_doctype(dt,year,fyi_doctype)
                                            #Copies the old document to the DV/Conv folders
                                            copyfile(doc_path,new_path)
                                            conv_count += 1
                                            if conv_count == 11:
                                                conv_count = 1

                                    #Otherwise, the document will not only be missing from the outfile, but it will print a message with insight fields to the user.
                                    else:
                                        print 'Path: ' + fyi_fullpath
                                        print 'Docdate: ' + fyi_docdate
                                        print 'Doctype: ' + fyi_doctype
                                        print 'Note field from ' + index_file + ': ' + note
                                        print 'Executable: ' + ex
                                        print

        #Grabs the time of the end of the conversion
        end = datetime.now()
        ft = end.strftime("%m/%d/%Y   %H:%M:%S")
        #Prints message that the conversion has been finished.
        print 'Kodata to IDM conversion has finished at ' + ft +'\n\n'
        #Will print a message of the doccount as well as a warning to check that there weren't any missing documents from above.
        print str(doccount) + ' documents have been converted. If there are any rows printed above, that means it is missing a docdate or doctype. Please research further if there any errors.'
        print
        #Calls the compare_counts method. This is used to help validate and make life easier.
        compare_counts()

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print('ERROR: ',exc_type, fname, exc_tb.tb_lineno,e)
        return






if __name__=="__main__":
    main()
