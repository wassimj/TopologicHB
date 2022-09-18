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
    st.header(account['id'])
    user = auth_user('auth-user', api_client)
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
    download_sql(api_client=api_client, owner=account, project=project, run_id=run['id'])
#api_key = st.text_input('api_key', type='password')

'''
if api_key:

st.header("Authenticated User")

acol1, acol2 = st.columns(2)

with acol1:
    user = auth_user('auth-user', api_client)
    if user is not None:
        st.json(user, expanded=False)

with acol2:
    account = select_account('select-account', api_client) or ''
    if account is not None and 'username' in account:
        st.json(account, expanded=False)




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
        job_id = st.session_state['daylight_job']
    elif job_type == "Energy Analysis":
        #job_id = st.session_state['energyanalysis_job']
        # For testing only. I am hard-coding the job id:
        job_id = "4f485478"
    run_index = st.number_input('run_index', value=0)
    output_name = st.text_input('output_name')
    submit_button = st.form_submit_button()

if submit_button:
    output = download_sql(owner, project, job_id, api_key)
    #sql_url = output['url']
    #st.write(sql_url)

 
 '''