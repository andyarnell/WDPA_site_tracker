##aim: join wdpa ids from poly and point featureclasses for each version and spit into a csv with duplicates removed##created by Andy Arnell 21/01/2015

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



##point to folder containing files - this script doesn't loop through
##rawFolder1 = r"L:\WDPA_Time_series\2003-2009_WDPA_VERSIONS"
rawFolder1 = r"L:\WDPA_Time_series\2010-2014_WDPA_VERSIONS\2014\WDPA_Sept2014_Public.gdb"

outFolder = r"L:\WDPA_Time_series\andy_working_files"

arcpy.env.workspace = rawFolder1

#####not needed as not looping through folders
#wkspceList=arcpy.ListWorkspaces("*","Folder")
# Open a file
##path = rawFolder1
##wkspceList = os.listdir( path )
##wkspceList=[x[0] for x in os.walk(path)]
##print wkspceList


#######make list of possible substrings to search with for polygon and point featureclasses and the prefix for the wdpa file
a=["poly","pol","polys","polygon","polygons"]
aupper=[x.upper() for x in a]
atitle=[x.title() for x in a]
shapeType1List=a + atitle # +aupper
print shapeType1List

a=["pt","pts","pnt","pnts","point","points"]
aupper=[x.upper() for x in a]
atitle=[x.title() for x in a]
shapeType2List=a + atitle # + aupper
print shapeType2List

#wdpa featureclass prefix list
a=["wdpa","international"]#,"national","nat","int"]
aupper=[x.upper() for x in a]
atitle=[x.title() for x in a]

wildCardList = a ##aupper+atitle
print wildCardList

#the name of wdpa id field (seems to be either wdpaid ,wdpa_id, or site_code (all upper case) - uncomment relevant one as required
fieldID ="WDPAID"
##fieldID ="WDPA_ID"
##fieldID = "SITE_CODE"


#set workspace as main folder as not looping through folders for this script
wkspce=rawFolder1

##looping through list of names for polygon, point and prefix for featureclass within folder/gdb of choice (rawFolder1)
for shapeType1 in shapeType1List:
    for shapeType2 in shapeType2List:
        for wildCard in wildCardList:
            ##commented out 2 lines as not looping through folders        
            ##for wkspce in wkspceList:
            ##arcpy.env.workspace = wkspce
            print wkspce
            srchStr1="*{0}*".format(shapeType1)
            srchStr2="*{0}*".format(shapeType2)
            print srchStr1
            print srchStr2
            #list all feature classes in folders using substrings and wildcards (*)
            fcList1=arcpy.ListFeatureClasses("*"+wildCard+"*"+shapeType1+"*")
            fcList2=arcpy.ListFeatureClasses("*"+wildCard+"*"+shapeType2+"*")
            print fcList1
            print fcList2
            for fc1 in fcList1:
                for fc2 in fcList2:
                    fc1Edit=str(fc1)
                    fc2Edit=str(fc2)
                    #change names from poly and point into shape so consistent
                    fc1Str=fc1Edit.replace(shapeType1,"shape")
                    fc2Str=fc2Edit.replace(shapeType2,"shape")
                    if fc1Str==fc2Str:
                        beginTime2 = time.clock()
                        try:
                            cursor=arcpy.da.SearchCursor(fc1,[fieldID]) ##make a search cursor to select all from field for featureclass fc1: fieldID
                            ls1=list()
                            ##loop through rows in search cursor and append to a second list for polygon files(ls1)
                            for row in cursor:
                                zval = (row[0])
                                #print zval #---if want to see wdpa ids then uncomment next line - but this will take tiem to run
                                ls1.append(zval)
                            cursor1=arcpy.da.SearchCursor(fc2,[fieldID]) ##make a search cursor to select all from field for featureclass fc2: fieldID
                            ls2=list()
                            ##loop through rows in search cursor and append to a second list for point files(ls2)
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
                            ls=ls1+ls2##combine the two lists of wdpa ids into one
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
   

        

            
                
                
                
            



