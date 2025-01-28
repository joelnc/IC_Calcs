#############################################################################
#############################################################################
# Import arcpy module
import arcpy
import customFuns as cf # for query builder
import shapefile # to read area out of dbf stats file
import pandas as pd # to write csv of summary results 

#############################################################################
# Set data and directory paths

# Set some hard paths for use below
culvDir = "d:/ArcpyOutput/monitDelin/oneOffDelins/Culverts/"
localDir = culvDir
sdwPath = "S:/Public/CityGIS/ArcSDE/connections/sdw.sde/"

# Set arcpy env
arcpy.env.workspace = culvDir

# Point at sdw paths for IC data 
dbCommercial = sdwPath + "sdw.DBO.ImperviousSurfaceNSF_py"
dbResidential = sdwPath + "sdw.DBO.ImperviousSurfaceSingleFamily_py"
dbOther = sdwPath + "sdw.DBO.ImperviousSurfaceOther_py"

arcpy.env.overwriteOutput = True # overwrite files

#############################################################################
# Feed in full path
def calcDissolveIC(watershedShape):
    """Fun to take a watershed shape, clip impervious, merge, dissolve, 
    recalculate, and then sum total IC, returned in acres """

    # Clips the 3 IC layers to watershed, storing results in memory
    commercial_clip = "in_memory\\commercial_clip"
    residential_clip = "in_memory\\residential_clip"
    other_clip = "in_memory\\other_clip"
    arcpy.Clip_analysis(dbCommercial, watershedShape, "in_memory\\commercial_clip")
    arcpy.Clip_analysis(dbResidential, watershedShape, "in_memory\\residential_clip")
    arcpy.Clip_analysis(dbOther, watershedShape, "in_memory\\other_clip")

    # Perform a merge between the 3 IC layers.
    mergeResult = watershedShape[:-4] + "_IC.shp"
    arcpy.Merge_management([commercial_clip, residential_clip, other_clip],
                           mergeResult)

    # Dissolve result via feature layer conversion
    dissolvedResult = mergeResult[:-4] + "_Dis.shp"
    arcpy.MakeFeatureLayer_management(mergeResult, "tempLayer")
    arcpy.management.Dissolve("tempLayer", dissolvedResult,
                              "", "",  "SINGLE_PART")

    # Tack on area in acres
    arcpy.AddGeometryAttributes_management(dissolvedResult, "AREA", "", "ACRES")

    # Sum area field to dbf table 
    statTable = watershedShape[:-4] + "_Stats.dbf"
    arcpy.Statistics_analysis(dissolvedResult, statTable,
                             [["POLY_AREA", "SUM"]], "")

    # Extract SUM_POLY_A, could probably use Pandas to read table instead 
    test = shapefile.Reader(statTable)
    icAcres = test.record(0)[1]  # 1st rec, 2nd field (area)

    del commercial_clip; del residential_clip
    del other_clip; del mergeResult
    del dissolvedResult

    return(icAcres)

# Run one local file
# calcDissolveIC("c:/Users/95218/Python/TMDL_IC_Calcs/LONG.shp")
calcDissolveIC(culvDir + "paw_subs_merge.shp")

#############################################################################
# Loop over all common themes watershed shapes
wBasins = "d:/ArcpyOutput/monitDelin/oneOffDelins/Culverts/IC_Dump/McMullen.shp"

# Init some lists to capture results on the fly 
wshed_list =[]
wshedArea_list = []
IC_area_list = []

# Loop, select watershed and write shp, then run IC fun
# with arcpy.da.SearchCursor(wBasins, ["OBJECTID", "fName", "Shape.STArea()"]) as cursor:
with arcpy.da.SearchCursor(wBasins, ["OBJECTID", "fName", "Shape_Area"]) as cursor:
    for row in cursor:
        # Populate gridCode for basin
        currWshed = row[1]
        wshedArea = float(row[2])/43560
        print(currWshed)

        # Append stuff to lists
        wshed_list.append(currWshed)
        wshedArea_list.append(wshedArea)

        # Create temporary watershed layer in memory
        tempWsheds = "in_memory\\wsheds"
        arcpy.MakeFeatureLayer_management(wBasins, tempWsheds)

        # Select the Current Watershed
        sel_Wshed = cf.buildWhereClause(tempWsheds, "fName", currWshed)
        arcpy.SelectLayerByAttribute_management(
            tempWsheds, "NEW_SELECTION", sel_Wshed)

        # new shp
        outShape = culvDir + "IC_Dump/" + currWshed + ".shp"
        arcpy.CopyFeatures_management(tempWsheds, outShape)

        # compute ic layer
        icAcres = calcDissolveIC(outShape)
        IC_area_list.append(icAcres)

        print(icAcres)
        print(wshedArea)
        icPct = icAcres/wshedArea
        print(icPct)

        del outShape; del sel_Wshed; del currWshed; del tempWsheds


# Compute impervious percent from output lists
icFrac = [x / y for x, y in zip(IC_area_list, wshedArea_list)] 
icPct = [z * 100 for z in icFrac]

# Wrap lists into panda df
outputDataFrame = pd.DataFrame(
    {'Watershed': wshed_list,
     'Watershed Acres': wshedArea_list,
     'Percent IC': icPct,
     'Impervious Acres': IC_area_list
     })

# Write csv
outputDataFrame.to_csv(culvDir + "IC_Dump/summary_table_3.csv", index=False)

