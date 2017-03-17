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

print "Setting local parameters and inputs"

# Check out the ArcGIS Spatial Analyst extension license
arcpy.CheckOutExtension("Spatial")

env.overwriteOutput = True

beginTime = time.clock()

##point to fodler to loop through and find all subfidlers within it (N.B. point to folder above the ones you are interested in)
rawFolder1 = r"H:\WDPA_Time_series\2010-2014_WDPA_VERSIONS\2010\April2010"

##rawFolder1 = r"L:\WDPA_Time_series\Ed's_working_files\temp_WDPA_output_v1_02.gdb"

##where output csvs are placed
outFolder = r"H:\WDPA_Time_series\andy_working_files"

rawFolder1 = r"C:\Data\wdpa_site_tracker\raw\1512_December_2015\WDPA_Dec2015_Public\WDPA_Dec2015_Public.gdb"


outFolder = r"C:\Data\wdpa_site_tracker\scratch"

#set environment (where to look to list subfolders)
arcpy.env.workspace = rawFolder1

# make list of all subfodlers and gdbs
path = rawFolder1
wkspceList = os.listdir( path )
wkspceList=[x[0] for x in os.walk(path)]
print wkspceList

#######make list of possible substrings to search with for polygon and point featureclasses and the prefix for the wdpa file

a=["poly","pol","polys"]
aupper=[x.upper() for x in a]
atitle=[x.title() for x in a]
shapeType1List=a#+ atitle  +aupper
print shapeType1List

a=["point","points","pnt","pnts","pt","pts"]
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
fieldID ="""'WDPAID','NAME','DESIG_ENG','PARENT_ISO3'"""


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
                print "searching for field in featureclass called: " +fieldID
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
                            try:
                                cursor=arcpy.da.SearchCursor(fc1,[fieldID])##make a search cursor to select all from field for featureclass fc1: fieldID
                                ls1=list()
                                #print ls1
                                ##loop through rows in search cursor and append to a second list for polygon files(ls1)
                                for row in cursor:
                                    zval = (row[0])
                                    #print zval #---if want to see wdpa ids then uncomment next line - but this will take tiem to run
                                    ls1.append(zval)
                                cursor1=arcpy.da.SearchCursor(fc2,[fieldID]) ##make a search cursor to select all from field for featureclass fc2: fieldID
                                ls2=list()
                                for row in cursor1:
                                    zval = (row[0])
                                    ls2.append(zval)
                                #do some count checking between ls1 and ls2 (polygons and points) before and after removing duplicates
                                print "ls1before: "+str(len(ls1))+shapeType1
                                ls1=list(set(ls1))
                                print "ls1after: "+str(len(ls1))+shapeType1
                                print "ls2before: "+str(len(ls2))+shapeType2
                                ls2=list(set(ls2))
                                print "ls2after: "+str(len(ls2))+shapeType2
                                ls=ls1+ls2 ##combine the two lists of wdpa ids into one
                                print "lsbefore:"+str(len(ls))+"CombinedPolyPoint" #print number of wdpa ids for polygons and poitns combined before removing duplicates
                                print wkspce
                                prefix=str(wkspce).rsplit('\\', 1) #get name of parent folder that file is contained in
                                prefix=str(prefix[-1:]).strip("""'[]'""")
                                print prefix
                                txtFile1=outFolder+"/preDuplRem_{0}_{1}.csv".format(prefix,fc1Str) #name and location of output file for wdpaids before duplicate removal 
                                
                                outFile1 = open(txtFile1, "w")#open csv (preDuplRem) to write into
                                for ids in ls:
                                    outFile1.write(str(ids) + "\n")#write to csv with a line in between each
                                ls=list(set(ls))#remove duplicates from combined (polygons and points) list of wdpa ids
                                print "lsafter:"+str(len(ls))+"CombinedPolyPoint"#print number of wdpa ids for polygons and poitns combined after removing duplicates
                                txtFile2=outFolder+"/postDuplRem_{0}_{1}.csv".format(prefix,fc1Str)#name and location of output file for wdpaids after duplicate removal 
                                outFile2 = open(txtFile2, "w")#open csv (postDuplRem) to write into
                                outFile1.close()
                                for ids in ls:
                                    outFile2.write(str(ids) + "\n")#write to csv with a line in between each
                                outFile2.close()#close csv
                            except:
                                print "ERROR - "+fieldID+"_not present - skipping..." #if wdpa id field (fieldID) is not correct print error message
                            print "Finished processing featureclass: {0} in {1} minutes \n".format(fc1Str,str(round(((time.clock() - beginTime2)/60),2)))

print "Finished processing"
print "Total time elapsed: {0} minutes".format(str(round(((time.clock() - beginTime)/60),2)))
   

        

            
                
                
                
            



