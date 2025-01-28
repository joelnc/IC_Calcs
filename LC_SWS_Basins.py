,#############################################################################
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

# Point at dissolved supermetric layer then shape to feature
dissSuperMet = "D:/ArcpyOutput/monitDelin/oneOffDelins/DissolvedTotalIC_2023.shp"

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

    ## New stuff. Need to clip IC to supermetric. Sum that. Pass that number
    ## Can then do math by diff in next loop given total ic and treated IC

    ## Ok, clip the shapefile of dissovled watershed ic to the supermetric 
    treated_clip = "in_memory\\treated_clip"
    arcpy.Clip_analysis(dissolvedResult, dissSuperMet, "in_memory\\treated_clip")

    # Tack on area in acres
    arcpy.AddGeometryAttributes_management(treated_clip, "AREA", "", "ACRES")

    # Sum area field to dbf table 
    statTable2 = watershedShape[:-4] + "_Stats2.dbf"
    arcpy.Statistics_analysis(treated_clip, statTable2,
                              [["POLY_AREA", "SUM"]], "")

    test2 = shapefile.Reader(statTable2)
    print(len(test2))
    if len(test2) == 0:
        print("None")
        icAcresTx = 0
    else:
        print("Some!")
        icAcresTx = test2.record(0)[1]  # 1st rec, 2nd field (area)

    del commercial_clip; del residential_clip
    del other_clip; del mergeResult
    del dissolvedResult; del treated_clip

    return(icAcres, icAcresTx)



#############################################################################
# Loop over all common themes watershed shapes
## Full
wBasins = "D:/ArcpyOutput/monitDelin/oneOffDelins/LC_SubsInCty.shp"

## troubleshooting subset
# wBasins = "d:/ArcpyOutput/monitDelin/oneOffDelins/LC_SubsInCty_Trouble.shp"


# Init some lists to capture results on the fly 
wshed_list =[]
wshedArea_list = []
IC_area_list = []
ICTX_area_list = []

## lists for treated IC, untreated IC, untreated %
## Maybe lists for EIA calcs? 


# this works...
# str('f') + "_" + str(!SWS!)

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

        # Copy selected current watershed to outShape as news
        outShape = culvDir + "IC_Dump/" + currWshed + ".shp"
        arcpy.CopyFeatures_management(tempWsheds, outShape)

        # Run IC function (Above)
        icAcres = calcDissolveIC(outShape)
        IC_area_list.append(icAcres[0])
        ICTX_area_list.append(icAcres[1])

        print(icAcres[0])
        print(wshedArea)
        icPct = icAcres[0]/wshedArea
        print(icPct)

        del outShape; del sel_Wshed; del currWshed; del tempWsheds


# Compute impervious percent from output lists
icFrac = [x / y for x, y in zip(IC_area_list, wshedArea_list)] 
icPct = [z * 100 for z in icFrac]
icPctMinus = [(x - y) / z for x, y, z in zip(IC_area_list, ICTX_area_list, wshedArea_list)]

# Wrap lists into panda df
outputDataFrame = pd.DataFrame(
    {'Watershed': wshed_list,
     'Watershed Acres': wshedArea_list,
     'Percent IC': icPct,
     'Percent IC Minus': icPctMinus,
     'Impervious Acres': IC_area_list
     })

# Write csv
outputDataFrame.to_csv(culvDir + "IC_Dump/summary_table_LSPC_v2.csv", index=False)

