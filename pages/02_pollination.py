#--------------------------
# IMPORT LIBRARIES
import streamlit as st
import json
import numpy as np
from numpy import arctan, pi, signbit, arctan2, rad2deg
from numpy.linalg import norm
import io

from pathlib import Path
from pollination_streamlit.api.client import ApiClient
from pollination_streamlit.interactors import NewJob, Recipe

import topologic

from topologicpy import TopologyByImportedJSONMK1, HBModelByTopology, TopologyAddApertures
#--------------------------
#--------------------------
# PAGE CONFIGURATION
st.set_page_config(
    page_title="Topologic HBJSON Test Application",
    page_icon="📊",
    layout="wide"
)
icon_column, title_column = st.columns([1,10], gap="small")
with icon_column:
    st.image("https://topologic.app/wp-content/uploads/2018/10/Topologic-Logo-250x250.png",width=100)
with title_column:
    st.title("Topologic <> Pollination Test App")

def add_recipe_to_job(new_job, recipe_arguments, recipe_artifacts) -> NewJob:
    """Add recipe arguments and artifacts to a job.

    args:
        new_job: A NewJob object.
        recipe_arguments: A dictionary of recipe arguments.
        recipe_artifacts: A dictionary of recipe artifacts where each items is a
            dictionary where the key is the name of the input on the recipe and the
            values are the paths to artifact and the path to the target folder on
            Pollination.

    returns:
        A NewJob object with the recipe arguments and artifacts added.
    """

    for key, val in recipe_artifacts.items():
        item = new_job.upload_artifact(
            val['file_path'], val['pollination_target_path'])
        recipe_arguments[key] = item

    new_job.arguments = [recipe_arguments]

    return new_job

#building_json_file = st.file_uploader("Upload Building", type="json", accept_multiple_files=False)

#building = None
#shadingCluster = None
#if building_json_file:
    #topologies = TopologyByImportedJSONMK1.processItem(building_json_file)
    #building = topologies[0]


building = st.session_state['Building']
apertureCluster = st.session_state['Apertures']
st.write("Building:",building)
st.write("Apertures:",apertureCluster)

new_building = TopologyAddApertures.processItem([building, apertureCluster, True, 0.0001, "Face"])
st.write("New Building:", new_building)
shadingCluster = None
if new_building:
    hbmodel = HBModelByTopology.processItem(tpBuilding=new_building,
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

    hbjson_string = json.dumps(hbmodel.to_dict())
    btn = st.download_button(
            label="Download HBJSON file",
            data=hbjson_string,
            file_name="topologic_hbjson.hbjson",
            mime="application/json"
        )



with st.form('daylight-factor-job'):

    st.markdown('Pollination credentials')
    api_key = st.text_input(
        'Enter Pollination API key', type='password')
    owner = st.text_input('Project Owner')
    st.markdown('---')

    st.markdown('Job inputs')
    project = st.text_input('Project Name')
    job_name = st.text_input('Job Name')
    job_description = st.text_input('Job Description')
    st.markdown('---')

    st.markdown('Recipe selection')
    recipe_owner = st.text_input('Recipe Owner', value='ladybug-tools')
    recipe_name = st.text_input('Recipe Name', value='daylight-factor')
    recipe_tag = st.text_input('Recipe Version', value='latest')
    st.markdown('---')

    st.markdown('Recipe inputs')
    # TODO: This will change based on the recipe you select
    cpu_count = st.number_input('CPU Count', value=50)
    grid_filter = st.text_input('Grid Filter', value='*')
    min_sensor_count = st.number_input('Min Sensor Count', value=200)
    #hbjson_data = st.file_uploader('Upload HBJSON')
    rad_parameters = st.text_input('Rad Parameters',
                                   value='-ab 2 -aa 0.1 -ad 2048 -ar 64')
    # TODO: change ends

    submit_button = st.form_submit_button(
        label='Submit')

    if submit_button:
        # create HBJSON file path
        hbjson_file = Path('.', 'model.hbjson')
        # write HBJSON file
        hbjson_file.write_bytes(hbjson_string.encode('utf-8'))

        # recipe inputs
        # TODO: This will change based on the recipe you select
        arguments = {
            'cpu-count': cpu_count,
            'grid-filter': grid_filter,
            'min-sensor-count': min_sensor_count,
            'radiance-parameters': rad_parameters,
        }

        # recipe inputs where a file needs to be uploaded
        artifacts = {
            'model': {'file_path': hbjson_file, 'pollination_target_path': ''}
        }
        # TODO: change ends

        api_client = ApiClient(api_token=api_key)
        recipe = Recipe(recipe_owner, recipe_name, recipe_tag, api_client)
        new_job = NewJob(owner, project, recipe, name=job_name,
                         description=job_description, client=api_client)
        new_job = add_recipe_to_job(new_job, arguments, artifacts)
        job = new_job.create()