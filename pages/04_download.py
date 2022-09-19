import streamlit as st
from pollination_streamlit.selectors import get_api_client
from pollination_streamlit_io import auth_user, select_account, select_project, select_study, select_run
import pollination_sdk
import json


def download_sql(api_client, owner, project, run_id: str):
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
    path_to_file = "/runs/"+run_id+"/workspace/eplsout.sql"
    api_instance = pollination_sdk.ArtifactsApi(api_client)
    api_response = api_instance.download_artifact(owner, project, path=path_to_file)
    return api_response




api_client = get_api_client()
account = None
user = None
project = None
study = None
run = None

if api_client:
    account = select_account('select-account', api_client) or ''
    user = auth_user('auth_user', api_client)
if account and user:
    project = select_project('select-project', api_client, project_owner=user['username'])
if project:
    study = select_study(
                'select-study',
                api_client,
                project_name=project['name'],
                project_owner=user['username']
            )
if study:
    run = select_run(
                    'select-run',
                    api_client,
                    project_name=project['name'],
                    project_owner=user['username'],
                    job_id=study['id']
                )
if run:
    api_instance = pollination_sdk.RunsApi(api_client)
    path_to_file = "/runs/"+run['id']+"/workspace/eplsout.sql"
    api_response = api_instance.download_run_artifact(project['name'], run['id'], path=path_to_file)
    st.write(api_response)
