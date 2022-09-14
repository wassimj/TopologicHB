import zipfile
import streamlit as st
from pollination_streamlit.interactors import Job
from pollination_streamlit.api.client import ApiClient

def download_output(api_key: str, owner: str, project: str, job_id: str, run_index: int,
                    output_name: str, target_folder: str) -> None:
    """Download output from a job on Pollination.

    Args:
        api_key: The API key of the Pollination account.
        owner: The owner of the Pollination account.
        project: The name of the project inside which the job was created.
        job_id: The id of the job.
        run_index: The index of the run inside the job.
        output_name: The name of the output you wish to download. You can find the names
            of all the outputs either on the job page or on the recipe page.
        target_folder: The folder where the output will be downloaded.
    """
    job = Job(owner, project, job_id, ApiClient(api_token=api_key))
    run = job.runs[run_index]
    output = run.download_zipped_output(output_name)

    with zipfile.ZipFile(output) as zip_folder:
        zip_folder.extractall(target_folder)

def download_sql(api_key: str, owner: str, project: str, job_id: str):
    """Download artifact from a job on Pollination.

    Args:
        api_key: The API key of the Pollination account.
        owner: The owner of the Pollination account.
        project: The name of the project inside which the job was created.
        job_id: The id of the job.
        run_index: The index of the run inside the job.
        output_name: The name of the output you wish to download. You can find the names
            of all the outputs either on the job page or on the recipe page.
        target_folder: The folder where the output will be downloaded.
    """
    job = Job(owner, project, job_id, ApiClient(api_token=api_key))
    run = job.runs[0]
    run_id = run.id

    if output_name == 'sql':
        path_to_file = "/runs/"+run_id+"/workspace/eplsout.sql"
    return job.downloadJobArtifact(owner, project, job_id, path_to_file)

submit_button = None

with st.form('download-result'):
    api_key = st.text_input('api_key', type='password')
    owner = st.text_input('owner')
    project = st.text_input('project')
    job_names = ["Select a Job", "Daylight Factor", "Energy Analysis"]
    option = st.selectbox(
        'Select a Job',
        job_names)
    if option != "Select a Job":
        job_type = option
    if job_type == "Daylight Factor":
        job_id = st.session['daylight_job']
    elif job_type == "Energy Analysis":
        job_id = st.session['energyanalysis_job']
    run_index = st.number_input('run_index', value=0)
    output_name = st.text_input('output_name')
    submit_button = st.form_submit_button(
        label='Submit')

    if submit_button:
        output = download_sql(owner, project, job_id, api_key)
        sql_url = output['url']
        st.write(sql_url)

 