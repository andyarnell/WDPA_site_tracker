# -*- coding: cp1252 -*-
#####Aim: join wdpa ids from poly and point featureclasses for each version and spit into a csv with duplicates removed

##created by Andy Arnell 21/01/2015

##will loop through all subfolders and find polygons and point files within.
##this uses a list of names to identify polyongs and poitn files as wdpa naming is variable over time
##it also uses a list of wdpa id field names (the field the ids are stored in which are also variable)
##this can take some time to run due to numer of combinations possible
##N.B.the accompanying script for annual versions can be used to focus on single folders/gdbs where featureclassses are found - use this one for where need to get into subfolders 

print "Importing packages"
import os.path
import os, sys, string
import arcpy
from arcpy import env
from arcpy.sa import *
import glob
import string
import time
import csv
import io


class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

##    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
##        # Redirect output to a queue
##        self.queue = cStringIO.StringIO()
##        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
##        self.stream = f
##        self.encoder = codecs.getincrementalencoder(encoding)()
##
##    def writerow(self, row):
##        self.writer.writerow([s.encode("utf-8") for s in row])
##        # Fetch UTF-8 output from the queue ...
##        data = self.queue.getvalue()
##        data = data.decode("utf-8")
##        # ... and reencode it into the target encoding
##        data = self.encoder.encode(data)
##        # write to the target stream
##        self.stream.write(data)
##        # empty queue
##        self.queue.truncate(0)
##
##    def writerows(self, rows):
##        for row in rows:
##            self.writerow(row)
            
print "Setting local parameters and inputs"

# Check out the ArcGIS Spatial Analyst extension license
arcpy.CheckOutExtension("Spatial")

env.overwriteOutput = True

beginTime = time.clock()

####point to fodler to loop through and find all subfidlers within it (N.B. point to folder above the ones you are interested in)
#rawFolder1 = r"H:\WDPA_Time_series\2010-2014_WDPA_VERSIONS\2010\April2010"
#rawFolder1 = r"C:\Data\wdpa_site_tracker\raw\1512_December_2015\WDPA_Dec2015_Public\WDPA_Dec2015_Public.gdb"
#rawFolder1 = r"L:\WDPA_Time_series\Ed's_working_files\temp_WDPA_output_v1_02.gdb"
#rawFolder1= r"L:\WDPA_Time_series\2010-2014_WDPA_VERSIONS\2010\1002_February_2010\Jan-Feb10\WDPA_100210"
rawFolder1= r"C:\Data\wdpa_site_tracker\raw\2010\1004_April_2010"

####where output csvs are placed
#outFolder = r"H:\WDPA_Time_series\andy_working_files"
outFolder = r"C:\Data\wdpa_site_tracker\scratch"

#set environment (where to look to list subfolders)
arcpy.env.workspace = rawFolder1

# make list of all subfodlers and gdbwriterowss
path = rawFolder1
wkspceList = os.listdir( path )
wkspceList=[x[0] for x in os.walk(path)]
print wkspceList

#######make list of possible substrings to search with for polygon and point featureclasses and the prefix for the wdpa file

a=["poly","pol","polys"]
aupper=[x.upper() for x in a]
atitle=[x.title() for x in a]
shapeType1List=a + atitle  +aupper
print shapeType1List

a=["point","points","pnt","pnts","pt","pts"]
aupper=[x.upper() for x in a]
atitle=[x.title() for x in a]


shapeType2List=a + atitle +aupper
print shapeType2List

#wdpa featureclass prefix list
a=["wdpa","international"]#,"national","nat","int"]
aupper=[x.upper() for x in a]
atitle=[x.title() for x in a]

wildCardList = a +aupper
print wildCardList

#the name of wdpa id field (seems to be either wdpaid ,wdpa_id, or site_code (all upper case) - uncomment relevant one as required

#fieldID ="WDPAID"
fields1 =['WDPAID','NAME','DESIG_ENG','DESIG_TYPE','ISO3','PARENT_ISO3']
fields2 =['WDPAID','NAME','DESIG_ENG','DESIG_TYPE','ISO3']
fields3 =['WDPAID','NAME','DESIG_ENG','DESIG_TYPE','COUNTRY']
fields4 =['WDPA_ID','NAME','DESIG_ENG','DESIG_TYPE','COUNTRY']
fields5 =['WDPA_ID','NAME','DESIG_ENG','DESIG_TYPE','COUNTRY']
fields6 =['SITE_ID','NAME_ENG','DESIG_ENG','SITE_TYPE','COUNTRY']


#fields =['WDPAID','NAME','DESIG_ENG','DESIG_TYPE','ISO3','PARENT_ISO3']
##
fldCombos=[fields6,fields5,fields4,fields3,fields2,fields1]
##
for fields in fldCombos:
    print fields     

##looping through list of names for polygon (shapeType1List), point(shapeType2List) and prefix (wildCardList) for featureclass within all subfolders/gdb within the rawFolder1
for shapeType1 in shapeType1List:
    for shapeType2 in shapeType2List:
        for wildCard in wildCardList:
                        
            for wkspce in wkspceList:
                arcpy.env.workspace = wkspce
                print wkspce
                srchStr1="*{0}*".format(shapeType1)
                srchStr2="*{0}*".format(shapeType2)
                print "searching for polygon featureclass with substring: " +srchStr1
                print "searching for point featureclass with substring: " +srchStr2
                #print "searching for field in featureclass called: " +fields
                #list all feature classes in folders using substrings and wildcards (*)
                fcList1=arcpy.ListFeatureClasses("*"+wildCard+"*"+shapeType1+"*")
                fcList2=arcpy.ListFeatureClasses("*"+wildCard+"*"+shapeType2+"*")
                print fcList1
                print fcList2
                for fc1 in fcList1:
                    for fc2 in fcList2:
                        #fc1Str=between(fc1, "poly",".")
                        #fc2Str=between(fc2, "point",".")
                        fc1Edit=str(fc1)
                        fc2Edit=str(fc2)
                        #change names from poly and point into shape so consistent
                        fc1Str=fc1Edit.replace(shapeType1,"shape")
                        fc2Str=fc2Edit.replace(shapeType2,"shape")
                        #print fc1Str
                        #print fc2Str
                        if fc1Str==fc2Str:
                            beginTime2 = time.clock()
                            prefix=str(wkspce).rsplit('\\', 1) #get name of parent folder that file is contained in
                            prefix=str(prefix[-1:]).strip("""'[]'""")
                            print (prefix)
                            
                            for fields in fldCombos:
                                print fields
                                i=0
                                for field in fields:
                                    fcFields1 = arcpy.ListFields(fc1,field)
                                    fcFields2 = arcpy.ListFields(fc2,field)
                                    if len(fcFields1) != 1 or len(fcFields2) !=1:
                                        print "field missing"
                                    else:
                                        i+=1
                                        print "field present"
                                print "number of fields present in featureclass:"+str(i)
                                print "number of fields present in field list:"+str(len(fields))
                                if i != len(fields):
                                    print "some fields missing"
                                else:
                                    print "all fields present"                                    
                                    print fields
                                    CSVFile1 =outFolder+"/preDuplRem_{0}_{1}.csv".format(prefix,fc1Str)
                                    with io.open(CSVFile1, 'w',encoding='utf-8') as csvfile:
                                        #csvfile.write(','.join(fields))
                                        with arcpy.da.SearchCursor(fc1, fields) as cursor1:
                                            for row in cursor1:
                                                row1 = list()

                                                for item in row:
                                                    if isinstance(item, unicode):
                                                        row1.append("\"" + item + "\"")
                                                    else:
                                                        row1.append(str(item))
                                                #print ','.join(row1)
                                                csvfile.write(','.join(row1)+"\n")
                                    csvfile.close()
                                    #CSVFile2 =outFolder+"/preDuplRem_{0}_{1}.csv".format(prefix,fc1Str)
                                    with io.open(CSVFile1, 'a',encoding='utf-8') as csvfile:
                                        with arcpy.da.SearchCursor(fc2, fields) as cursor2:
                                            for row in cursor2:
                                                row1 = list()

                                                for item in row:
                                                    if isinstance(item, unicode):
                                                        row1.append("\"" + item + "\"")
                                                    else:
                                                        row1.append(str(item))
                                                #print ','.join(row1)
                                                csvfile.write(','.join(row1)+"\n")
                                    csvfile.close()
                                    
##                                    
####                                    except:
####                                        print "ERROR - fields_not present - skipping..." #if wdpa id field (fieldID) is not correct print error message
####                                        print "Finished processing featureclass: {0} in {1} minutes \n".format(fc1Str,str(round(((time.clock() - beginTime2)/60),2)))
####                                    try:
##                                    with open(CSVFile1, 'ab') as csvfile:
##                                        spamwriter = csv.writer(csvfile, delimiter=',',quoting=csv.QUOTE_MINIMAL)
##                                        #spamwriter = UnicodeWriter(csvfile)
##                                        with arcpy.da.SearchCursor(fc2, fields) as cursor2:
##                                            for row in cursor2:
##                                                #row=list(row)
##                                                #row = [v.decode('latin-1') if isinstance(v, str) else v for v in list(row)]
##                                                #spamwriter.writerow(row[1].encode('utf8'))
##                                                spamwriter.writerows(row)
##                                                                                                
##                                    csvfile.close()
####                                    except:
##                                    print "ERROR - fields_not present - skipping..." #if wdpa id field (fieldID) is not correct print error message
##                                    print "Finished processing featureclass: {0} in {1} minutes \n".format(fc1Str,str(round(((time.clock() - beginTime2)/60),2)))
##                                
print "Finished processing"
print "Total time elapsed: {0} minutes".format(str(round(((time.clock() - beginTime)/60),2)))
   

        

            
                
                
                
            



