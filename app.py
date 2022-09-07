#--------------------------
# IMPORT LIBRARIES
import streamlit as st
import json
import numpy as np
from numpy import arctan, pi, signbit, arctan2, rad2deg
from numpy.linalg import norm
import io

# import topologic
# This requires some checking of the used OS platform to load the correct version of Topologic
import sys
import os
from sys import platform
if platform == 'win32':
    os_name = 'windows'
else:
    os_name = 'linux'
sitePackagesFolderName = os.path.join(os.path.dirname(os.path.realpath(__file__)), "bin", os_name)
topologicFolderName = [filename for filename in os.listdir(sitePackagesFolderName) if filename.startswith("topologic")][0]
topologicPath = os.path.join(sitePackagesFolderName, topologicFolderName)
sys.path.append(topologicPath)
import topologic

from topologicpy import TopologyByImportedJSONMK1, HBModelByTopology
#--------------------------
#--------------------------
# PAGE CONFIGURATION
st.set_page_config(
    page_title="Topologic HBJSON Test Application",
    page_icon="📊",
    layout="wide"
)
building_json_file = st.file_uploader("", type="json", accept_multiple_files=False)
shading_json_file = st.file_uploader("", type="json", accept_multiple_files=False)

building = None
shadingCluster = None
if building_json_file:
    topologies = TopologyByImportedJSONMK1.processItem(building_json_file)
    building = topologies[0]

if shading_json_file:
    topologies = TopologyByImportedJSONMK1.processItem(shading_json_file)
    shadingCluster = topologies[0]

if building:
    hbmodel = HBModelByTopology.processItem(tpBuilding=building,
                    tpShadingFacesCluster=shadingCluster,
                    buildingName = "Generic_Building",
                    defaultProgramIdentifier = "Generic Office Program",
                    defaultConstructionSetIdentifier = "Default Generic Construction Set",
                    coolingSetpoint = 25.0,
                    heatingSetpoint = 20.0,
                    humidifyingSetpoint = 30.0,
                    dehumidifyingSetpoint = 55.0,
                    roomNameKey = "Name",
                    roomTypeKey = "Type")

    hbjson_string = json.dumps(hbModel.to_dict())
    with open("topologic_hbjson.hbjson", "r") as file:
        btn = st.download_button(
                label="Download HBJSON file",
                data=hbjson_string,
                file_name="topologic_hbjson.hbjson",
                mime="application/json"
            )



