import streamlit as st
from pollination_streamlit_io import auth_user, select_account, select_project, select_study, select_run
import pollination_sdk
from pollination_streamlit.interactors import Job
from pollination_streamlit.api.client import ApiClient
from pollination_streamlit.selectors import (get_api_client, job_selector)
import json
import zipfile

def download_output(api_key: str, owner: str, project: str, run,
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
    #job = Job(owner, project, job_id, ApiClient(api_token=api_key))
    #run = study.runs[run_index]
    output = run.download_zipped_output(output_name)

    with zipfile.ZipFile(output) as zip_folder:
        zip_folder.extractall(target_folder)


api_client = get_api_client()
account = None
user = None
project = None
study = None
run = None


api_client = get_api_client()
study = job_selector(api_client)


'''
if api_client:
    account = select_account('select-account', api_client) or ''
    user = auth_user('auth_user', api_client) or ''
if account and user:
    project = select_project('select-project', api_client, project_owner=user['username']) or ''
if project:
    study = job_selector(api_client)
if study:
    run = select_run(
                    'select-run',
                    api_client,
                    project_name=project['name'],
                    project_owner=user['username'],
                    job_id=study['id']
                ) or ''
if run:
    api_instance = pollination_sdk.RunsApi(api_client)
    path_to_file = "/runs/"+run['id']+"/workspace/eplsout.sql"

    download_output(api_key=api_key, owner=account['username'], project=project['name'], run=run,
                    output_name='eplsout.sql', target_folder='.')

def handleSelectArtifact():
    bytes = st.session_state['sel_artifact'].download().read()
    st.session_state['text'] = bytes.decode('utf8')

def formatArtifact(artifact):
    if 'key' in artifact.__dict__:
        return artifact.key
    else:
        return ''

if 'text' not in st.session_state:
    st.session_state['text'] = ''

if 'artifacts' not in st.session_state:
    st.session_state['artifacts'] = []

def followArtifactTree(artifact_array):
    for artifact in artifact_array:
        if artifact.is_folder:
            followArtifactTree(artifact.list_children())
        else :
              st.session_state['artifacts'].append(artifact)
    
if study is not None:
    artifacts = study.list_artifacts()

    if artifacts is not None:
        followArtifactTree(artifacts)

st.selectbox(
  'Select an artifact', 
  options= st.session_state['artifacts'], 
  key='sel_artifact', 
  on_change=handleSelectArtifact, 
  format_func=formatArtifact
)

st.download_button(
    label='Download Text File', 
    data=st.session_state['text'], 
    file_name=st.session_state['sel_artifact'].key if st.session_state['sel_artifact'] is not None else '', 
    key='download-button',
    disabled=st.session_state['text'] == ''
)

    #api_response = api_instance.download_run_artifact(owner=account['username'], name=project['name'], run_id=run['id'], path=path_to_file)
    #st.write(api_response)
'''