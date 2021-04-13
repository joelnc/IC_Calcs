# Authorship: Original IC processing script given to Armando Jiminez in
# summer 2019 to add roof IC extraction.  Armando re-wrote original using
# arcpy.TabulateIntersection_analysis rather than my search cursor loop.  
# Expaneded below to include reg PctIC as well as rooftop, and to write out
# .json file.

#############################################################################
#############################################################################
# Import arcpy module
import arcpy
import pandas as pd
import os
import shutil


#############################################################################
# Set data and directory paths
# This variable can be changed to your directory containing the Reedy data
reedyGISDir = "G:/Water Quality/05 Planning, Research, Monitoring, & Modeling/Reedy-GIS-Share/"
arcpy.env.workspace = reedyGISDir + "imperviousCalculations/"
localDir = "c:/Users/95218/Python/TMDL_IC_Calcs/"

# Point at sdw paths for IC data 
sdwPath = "S:/Public/CityGIS/ArcSDE/connections/sdw.sde/"
dbCommercial = sdwPath + "sdw.DBO.ImperviousSurfaceNSF_py"
dbResidential = sdwPath + "sdw.DBO.ImperviousSurfaceSingleFamily_py"
dbOther = sdwPath + "sdw.DBO.ImperviousSurfaceOther_py"

arcpy.env.overwriteOutput = True

# Point at shapefiles
lsugar = localDir + "LSUGAR_merge.shp"
longCk = localDir + "LONG.shp"
sugar = localDir + "SUGAR_merge.shp"
mcalpine = localDir + "MCALPINE_merge.shp"
mckee = localDir + "MCKEE.shp"
steele = localDir + "STEELE.shp"
etj = localDir + "etj.shp"
rec = localDir + "testUptownRect.shp"

#############################################################################
## Uptown Rectangle Test

# Clip and merge City wide IC
wshed = rec
# Stores large files in memory
commercial_clip = "in_memory\\commercial_clip"
residential_clip = "in_memory\\residential_clip"
other_clip = "in_memory\\other_clip"

# Clips layers to Reedy
arcpy.Clip_analysis(dbCommercial, wshed, "in_memory\\commercial_clip")
arcpy.Clip_analysis(dbResidential, wshed, "in_memory\\residential_clip")
arcpy.Clip_analysis(dbOther, wshed, "in_memory\\other_clip")

# Perform a merge between the 3 IC layers. 
arcpy.Merge_management([commercial_clip, residential_clip, other_clip],
                       localDir + "recIc_test1.shp")

# Dissolve result via feature layer conversion
inFeatures = localDir + "recIc_test1.shp"
outFeatureClass = localDir + "recIc_test1_diss.shp"
arcpy.MakeFeatureLayer_management(inFeatures, "tempLayer")
arcpy.management.Dissolve("tempLayer", outFeatureClass,
                          "", "",  "SINGLE_PART")

# Tack on area in acres
arcpy.AddGeometryAttributes_management(outFeatureClass, "AREA", "", "ACRES")

# Delete
del commercial_clip; del residential_clip; del other_clip


#############################################################################
# Clip and merge City wide IC to ETJ
wshed = etj
# Stores large files in memory
commercial_clip = "in_memory\\commercial_clip"
residential_clip = "in_memory\\residential_clip"
other_clip = "in_memory\\other_clip"

# Clips layers to Reedy
arcpy.Clip_analysis(dbCommercial, wshed, "in_memory\\commercial_clip")
arcpy.Clip_analysis(dbResidential, wshed, "in_memory\\residential_clip")
arcpy.Clip_analysis(dbOther, wshed, "in_memory\\other_clip")

# Perform a merge between the 3 IC layers. Merged into reedyImpervious
mergeResult = localDir + "etjIc.shp"
arcpy.Merge_management([commercial_clip, residential_clip, other_clip],
                       mergeResult)

# Dissolve result via feature layer conversion
dissolvedResult = localDir + "etjIc_diss.shp"
arcpy.MakeFeatureLayer_management(mergeResult, "tempLayer")
arcpy.management.Dissolve("tempLayer", dissolvedResult,
                          "", "",  "SINGLE_PART")

# Tack on area in acres
arcpy.AddGeometryAttributes_management(dissolvedResult, "AREA", "", "ACRES")

# Delete
del commercial_clip; del residential_clip; del other_clip; del dissolvedResult

#############################################################################
# Clip and merge City wide IC to LSUGAR
wshed = lsugar
# Stores large files in memory
commercial_clip = "in_memory\\commercial_clip"
residential_clip = "in_memory\\residential_clip"
other_clip = "in_memory\\other_clip"

# Clips layers to Reedy
arcpy.Clip_analysis(dbCommercial, wshed, "in_memory\\commercial_clip")
arcpy.Clip_analysis(dbResidential, wshed, "in_memory\\residential_clip")
arcpy.Clip_analysis(dbOther, wshed, "in_memory\\other_clip")

# Perform a merge between the 2 IC layers. Merged into reedyImpervious
mergeResult = localDir + "lsugarIc.shp"
arcpy.Merge_management([commercial_clip, residential_clip, other_clip],
                       mergeResult)

# Dissolve result via feature layer conversion
dissolvedResult = localDir + "lsugarIc_diss.shp"
arcpy.MakeFeatureLayer_management(mergeResult, "tempLayer")
arcpy.management.Dissolve("tempLayer", dissolvedResult,
                          "", "",  "SINGLE_PART")

# Tack on area in acres
arcpy.AddGeometryAttributes_management(dissolvedResult, "AREA", "", "ACRES")

# Delete
del commercial_clip; del residential_clip; del other_clip; del dissolvedResult

#############################################################################
# Clip and merge City wide IC to MCKEE
wshed = mckee
# Stores large files in memory
commercial_clip = "in_memory\\commercial_clip"
residential_clip = "in_memory\\residential_clip"
other_clip = "in_memory\\other_clip"

# Clips layers to Reedy
arcpy.Clip_analysis(dbCommercial, wshed, "in_memory\\commercial_clip")
arcpy.Clip_analysis(dbResidential, wshed, "in_memory\\residential_clip")
arcpy.Clip_analysis(dbOther, wshed, "in_memory\\other_clip")

# Perform a merge between the 2 IC layers. Merged into reedyImpervious
mergeResult = localDir + "mckeeIc.shp"
arcpy.Merge_management([commercial_clip, residential_clip, other_clip],
                       mergeResult)

# Dissolve result via feature layer conversion
dissolvedResult = localDir + "mckeeIc_diss.shp"
arcpy.MakeFeatureLayer_management(mergeResult, "tempLayer")
arcpy.management.Dissolve("tempLayer", dissolvedResult,
                          "", "",  "SINGLE_PART")

# Tack on area in acres
arcpy.AddGeometryAttributes_management(dissolvedResult, "AREA", "", "ACRES")

# Delete
del commercial_clip; del residential_clip; del other_clip; del dissolvedResult


#############################################################################
# Clip and merge City wide IC to SUGAR 
wshed = sugar
# Stores large files in memory
commercial_clip = "in_memory\\commercial_clip"
residential_clip = "in_memory\\residential_clip"
other_clip = "in_memory\\other_clip"

# Clips layers to Reedy
arcpy.Clip_analysis(dbCommercial, wshed, "in_memory\\commercial_clip")
arcpy.Clip_analysis(dbResidential, wshed, "in_memory\\residential_clip")
arcpy.Clip_analysis(dbOther, wshed, "in_memory\\other_clip")

# Perform a merge between the 2 IC layers. Merged into reedyImpervious
mergeResult = localDir + "sugarIc.shp"
arcpy.Merge_management([commercial_clip, residential_clip, other_clip],
                       mergeResult)

# Dissolve result via feature layer conversion
dissolvedResult = localDir + "sugarIc_diss.shp"
arcpy.MakeFeatureLayer_management(mergeResult, "tempLayer")
arcpy.management.Dissolve("tempLayer", dissolvedResult,
                          "", "",  "SINGLE_PART")

# Tack on area in acres
arcpy.AddGeometryAttributes_management(dissolvedResult, "AREA", "", "ACRES")

# Delete
del commercial_clip; del residential_clip; del other_clip; del dissolvedResult

#############################################################################
# Clip and merge City wide IC to LONG 
wshed = longCk
# Stores large files in memory
commercial_clip = "in_memory\\commercial_clip"
residential_clip = "in_memory\\residential_clip"
other_clip = "in_memory\\other_clip"

# Clips layers to Reedy
arcpy.Clip_analysis(dbCommercial, wshed, "in_memory\\commercial_clip")
arcpy.Clip_analysis(dbResidential, wshed, "in_memory\\residential_clip")
arcpy.Clip_analysis(dbOther, wshed, "in_memory\\other_clip")

# Perform a merge between the 2 IC layers. Merged into reedyImpervious
mergeResult = localDir + "longIc.shp"
arcpy.Merge_management([commercial_clip, residential_clip, other_clip],
                       mergeResult)

# Dissolve result via feature layer conversion
dissolvedResult = localDir + "longIc_diss.shp"
arcpy.MakeFeatureLayer_management(mergeResult, "tempLayer")
arcpy.management.Dissolve("tempLayer", dissolvedResult,
                          "", "",  "SINGLE_PART")

# Tack on area in acres
arcpy.AddGeometryAttributes_management(dissolvedResult, "AREA", "", "ACRES")

# Delete
del commercial_clip; del residential_clip; del other_clip; del dissolvedResult


#############################################################################
# Clip and merge City wide IC to MCALPINE 
wshed = mcalpine
# Stores large files in memory
commercial_clip = "in_memory\\commercial_clip"
residential_clip = "in_memory\\residential_clip"
other_clip = "in_memory\\other_clip"

# Clips layers to Reedy
arcpy.Clip_analysis(dbCommercial, wshed, "in_memory\\commercial_clip")
arcpy.Clip_analysis(dbResidential, wshed, "in_memory\\residential_clip")
arcpy.Clip_analysis(dbOther, wshed, "in_memory\\other_clip")

# Perform a merge between the 2 IC layers. Merged into reedyImpervious
mergeResult = localDir + "mcalpineIc.shp"
arcpy.Merge_management([commercial_clip, residential_clip, other_clip],
                       mergeResult)

# Dissolve result via feature layer conversion
dissolvedResult = localDir + "mcalpineIc_diss.shp"
arcpy.MakeFeatureLayer_management(mergeResult, "tempLayer")
arcpy.management.Dissolve("tempLayer", dissolvedResult,
                          "", "",  "SINGLE_PART")

# Tack on area in acres
arcpy.AddGeometryAttributes_management(dissolvedResult, "AREA", "", "ACRES")

# Delete
del commercial_clip; del residential_clip; del other_clip; del dissolvedResult

#############################################################################
# Clip and merge City wide IC to MCALPINE 
wshed = steele
# Stores large files in memory
commercial_clip = "in_memory\\commercial_clip"
residential_clip = "in_memory\\residential_clip"
other_clip = "in_memory\\other_clip"

# Clips layers to Reedy
arcpy.Clip_analysis(dbCommercial, wshed, "in_memory\\commercial_clip")
arcpy.Clip_analysis(dbResidential, wshed, "in_memory\\residential_clip")
arcpy.Clip_analysis(dbOther, wshed, "in_memory\\other_clip")

# Perform a merge between the 2 IC layers. Merged into reedyImpervious
mergeResult = localDir + "steeleIc.shp"
arcpy.Merge_management([commercial_clip, residential_clip, other_clip],
                       mergeResult)

# Dissolve result via feature layer conversion
dissolvedResult = localDir + "steeleIc_diss.shp"
arcpy.MakeFeatureLayer_management(mergeResult, "tempLayer")
arcpy.management.Dissolve("tempLayer", dissolvedResult,
                          "", "",  "SINGLE_PART")

# Tack on area in acres
arcpy.AddGeometryAttributes_management(dissolvedResult, "AREA", "", "ACRES")

# Delete
del commercial_clip; del residential_clip; del other_clip; del dissolvedResult

