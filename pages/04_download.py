import streamlit as st
from pollination_streamlit.selectors import get_api_client
from pollination_streamlit_io import auth_user, select_account, select_project, select_study, select_run
import pollination_sdk
from pollination_streamlit.interactors import Job
from pollination_streamlit.api.client import ApiClient
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

api_key = st.text_input('api_key', type='password')
if api_key:
    api_client = ApiClient(api_token=api_key)
if api_client:
    account = select_account('select-account', api_client) or ''
    user = auth_user('auth_user', api_client) or ''
if account and user:
    project = select_project('select-project', api_client, project_owner=user['username']) or ''
if project:
    study = select_study(
                'select-study',
                api_client,
                project_name=project['name'],
                project_owner=user['username']
            ) or ''
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

    #api_response = api_instance.download_run_artifact(owner=account['username'], name=project['name'], run_id=run['id'], path=path_to_file)
    #st.write(api_response)
