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

from io import StringIO
#--------------------------
#--------------------------

def stringByUploadedFile(uploaded_file):
    return uploaded_file.getvalue().decode('utf-8')

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



hbjson_string = st.session_state['hbjson']
    


submitted = False

with st.form('energy-analysis'):

    #st.markdown('Pollination credentials')
    api_key = st.text_input(
        'Enter Pollination API key', type='password')
    owner = st.text_input('Project Owner')
    #st.markdown('---')

    st.markdown('Job inputs')
    project = st.text_input('Project Name')
    job_name = st.text_input('Job Name')
    job_description = st.text_input('Job Description')
    #st.markdown('---')

    st.markdown('Recipe selection')
    recipe_owner = st.text_input('Recipe Owner', value='ladybug-tools')
    recipe_name = st.text_input('Recipe Name', value='custom-energy-sim')
    recipe_tag = st.text_input('Recipe Version', value='latest')
    #st.markdown('---')

    #st.markdown('Recipe inputs')

    ddy_uploaded_file = st.file_uploader('Upload DDY File', type='ddy')
    epw_uploaded_file = st.file_uploader('Upload EPW File', type='epw')

    ddy_string = None
    epw_string = None

    submitted = st.form_submit_button('Submit')

if ddy_uploaded_file:
    ddy_string = stringByUploadedFile(ddy_uploaded_file)
    ddy_name = ddy_uploaded_file.name
if epw_uploaded_file:
    epw_string = stringByUploadedFile(epw_uploaded_file)
    epw_name = epw_uploaded_file.name
if submitted and ddy_string and epw_string:
    # create HBJSON file path
    hbjson_file = Path('.', 'topologic_model.hbjson')
    # write HBJSON file
    hbjson_file.write_bytes(hbjson_string.encode('utf-8'))

    # create DDY file path
    ddy_file = Path('.', ddy_name)
    # write DDY file
    ddy_file.write_bytes(ddy_string.encode('utf-8'))
    # create EPW file path
    epw_file = Path('.', epw_name)
    # write EPW file
    epw_file.write_bytes(epw_string.encode('utf-8'))

    # recipe inputs
    # TODO: This will change based on the recipe you select

    arguments = {
        'ddy': ddy_name,
        'epw': epw_name,
    }

    # recipe inputs where a file needs to be uploaded
    artifacts = {
        'model': {'file_path': hbjson_file, 'pollination_target_path': ''},
        'ddy': {'file_path': ddy_file, 'pollination_target_path': ''},
        'epw': {'file_path': epw_file, 'pollination_target_path': ''}
    }
    # TODO: change ends

    api_client = ApiClient(api_token=api_key)
    recipe = Recipe(recipe_owner, recipe_name, recipe_tag, api_client)
    new_job = NewJob(owner, project, recipe, name=job_name,
                        description=job_description, client=api_client)
    new_job = add_recipe_to_job(new_job, arguments, artifacts)
    job = new_job.create()
    if job:
        st.subheader("JOB HAS BEEN SUBMITTED. CHECK ITS PROGRESS ON POLLINATION CLOUD")
        st.write(dir(job))
        st.session['energyanalysis_job'] = job