#############################################################################
#############################################################################
# Import arcpy module
import arcpy

#############################################################################
# Set data and directory paths

# Set some hard paths for use below
reedyGISDir = "G:/Water Quality/05 Planning, Research, Monitoring, & Modeling/Reedy-GIS-Share/"
localDir = "c:/Users/95218/Python/TMDL_IC_Calcs/"
sdwPath = "S:/Public/CityGIS/ArcSDE/connections/sdw.sde/"

# Set arcpy env
arcpy.env.workspace = reedyGISDir + "imperviousCalculations/"

# Point at sdw paths for IC data 
dbCommercial = sdwPath + "sdw.DBO.ImperviousSurfaceNSF_py"
dbResidential = sdwPath + "sdw.DBO.ImperviousSurfaceSingleFamily_py"
dbOther = sdwPath + "sdw.DBO.ImperviousSurfaceOther_py"

arcpy.env.overwriteOutput = True # overwrite files

#############################################################################
# Long Creek

# Point at a local shapefile of Long Creek
wshed = localDir + "LONG.shp"

# Clips the 3 IC layers to watershed, storing results in memory
# Commercial
commercial_clip = "in_memory\\commercial_clip"
arcpy.Clip_analysis(dbCommercial, wshed, "in_memory\\commercial_clip")

# Residential
residential_clip = "in_memory\\residential_clip"
arcpy.Clip_analysis(dbResidential, wshed, "in_memory\\residential_clip")

# Other IC
other_clip = "in_memory\\other_clip"
arcpy.Clip_analysis(dbOther, wshed, "in_memory\\other_clip")


# Perform a merge between the 3 IC layers.
mergeResult = localDir + "LongCreekIC.shp"
arcpy.Merge_management([commercial_clip, residential_clip, other_clip],
                       mergeResult)

# Dissolve result via feature layer conversion
dissolvedResult = localDir + "LongCreekIC_diss.shp"
arcpy.MakeFeatureLayer_management(mergeResult, "tempLayer")
arcpy.management.Dissolve("tempLayer", dissolvedResult,
                          "", "",  "SINGLE_PART")

# Tack on area in acres
arcpy.AddGeometryAttributes_management(dissolvedResult, "AREA", "", "ACRES")

# Load resulting shapefile in ArcMap, sum POLY_AREA to get total IC in acres
