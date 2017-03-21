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


print "Setting local parameters and inputs"

# Check out the ArcGIS Spatial Analyst extension license
arcpy.CheckOutExtension("Spatial")

env.overwriteOutput = True

beginTime = time.clock()

####point to fodler to loop through and find all subfidlers within it (N.B. point to folder above the ones you are interested in)
#rawFolder1 = r"H:\WDPA_Time_series\2010-2014_WDPA_VERSIONS\2010\April2010"
rawFolder1 = r"C:\Data\wdpa_site_tracker\raw\1512_December_2015\WDPA_Dec2015_Public\WDPA_Dec2015_Public.gdb"
##rawFolder1 = r"L:\WDPA_Time_series\Ed's_working_files\temp_WDPA_output_v1_02.gdb"

####where output csvs are placed
#outFolder = r"H:\WDPA_Time_series\andy_working_files"
outFolder = r"C:\Data\wdpa_site_tracker\scratch"

#set environment (where to look to list subfolders)
arcpy.env.workspace = rawFolder1

# make list of all subfodlers and gdbs
path = rawFolder1
wkspceList = os.listdir( path )
wkspceList=[x[0] for x in os.walk(path)]
print wkspceList

#######make list of possible substrings to search with for polygon and point featureclasses and the prefix for the wdpa file

a=["poly"]#,"pol","polys"]
aupper=[x.upper() for x in a]
atitle=[x.title() for x in a]
shapeType1List=a#+ atitle  +aupper
print shapeType1List

a=["point"]#,"points","pnt","pnts","pt","pts"]
aupper=[x.upper() for x in a]
atitle=[x.title() for x in a]


shapeType2List=a#+ atitle +aupper
print shapeType2List

#wdpa featureclass prefix list
a=["wdpa","international"]#,"national","nat","int"]
aupper=[x.upper() for x in a]
atitle=[x.title() for x in a]

wildCardList = a +aupper
print wildCardList

#the name of wdpa id field (seems to be either wdpaid ,wdpa_id, or site_code (all upper case) - uncomment relevant one as required

#fieldID ="WDPAID"
fields =['WDPAID','NAME','DESIG_ENG','PARENT_ISO3']


#fieldID = "WDPA_ID"
##fieldID = "SITE_CODE"

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
                            try:
                                CSVFile1 =outFolder+"/preDuplRem_{0}_{1}.csv".format(prefix,fc1Str)
##                                with open(CSVFile1, 'w') as f1:
##                                    #bob=csv.writer(CSVFile1, delimiter=' ',quotechar='|', quoting=csv.QUOTE_MINIMAL)
##                                    f1.write('  '.join(fields)+'\n') 
##                                    with arcpy.da.SearchCursor(fc1, fields) as cursor1:
##                                        for row in cursor1:
##                                            print('{0}, {1}, {2}, {3}'.format(str(row[0]), str(row[1]),str(row[2]),str(row[3]) ))
##                                            f1.write('  '.join([str(r) for r in row])+'\n')
##                                f1.close()
                                with open(CSVFile1, 'wb') as csvfile:
                                    spamwriter = csv.writer(csvfile, delimiter=',',quoting=csv.QUOTE_MINIMAL)
                                    with arcpy.da.SearchCursor(fc2, fields) as cursor1:
                                        for row in cursor1:
                                            #row=[s.encode('utf-8') for s in row]
                                            #print('{0}, {1}, {2}, {3}'.format(str(row[0]), str(row[1]),str(row[2]),str(row[3]) ) )
                                            spamwriter.writerow((row))
                                            #writer.writerow(','.join([str(r) for r in row])+'\n')
                                            
                            except:
                                print "ERROR - fields_not present - skipping..." #if wdpa id field (fieldID) is not correct print error message
                                print "Finished processing featureclass: {0} in {1} minutes \n".format(fc1Str,str(round(((time.clock() - beginTime2)/60),2)))
##                            try:
##                                #CSVFile2 = r"c:\Data\wdpa_site_tracker\scratch\test2.csv"
##                                #with open(CSVFile2, 'w') as f2:
##                                with open(CSVFile1, 'a') as f2:
##                                    #f2.write(','.join(fields)+'\n') 
##                                    with arcpy.da.SearchCursor(fc2, fields) as cursor2:
##                                        for row in cursor2:
##                                            print('{0}, {1}, {2}, {3}'.format(str(row[0]), str(row[1]),str(row[2]),str(row[3]) ))
##                                            f2.write('  '.join([str(r) for r in row])+'\n')
##
##                                f2.close()
##                                #f1.close()
##                            except:
##                                print "ERROR - fields_not present - skipping..." #if wdpa id field (fieldID) is not correct print error message
##                                print "Finished processing featureclass: {0} in {1} minutes \n".format(fc1Str,str(round(((time.clock() - beginTime2)/60),2)))
                                
print "Finished processing"
print "Total time elapsed: {0} minutes".format(str(round(((time.clock() - beginTime)/60),2)))
   

        

            
                
                
                
            



