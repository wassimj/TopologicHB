#--------------------------
#IMPORT LIBRARIES
import requests
import random
import math
import string
#import streamlit
import streamlit as st
#specklepy libraries
from specklepy.api.client import SpeckleClient
from specklepy.api.credentials import get_account_from_token
from specklepy.api.client import SpeckleClient
from specklepy.api.credentials import get_default_account
from specklepy.api.credentials import get_account_from_token
from specklepy.transports.memory import MemoryTransport
from specklepy.api import operations
from specklepy.api.wrapper import StreamWrapper
from specklepy.api.resources.stream import Stream
from specklepy.transports.server import ServerTransport
from specklepy.objects.geometry import *
from specklepy.logging.exceptions import SpeckleException
from specklepy.objects.other import RenderMaterial

from specklepy.api.client import SpeckleClient
from specklepy.api.credentials import get_default_account
from specklepy.transports.memory import MemoryTransport
from specklepy.api import operations
from specklepy.api.wrapper import StreamWrapper
from specklepy.api.resources.stream import Stream
from specklepy.transports.server import ServerTransport
from specklepy.objects.geometry import *
from specklepy.logging.exceptions import SpeckleException
from specklepy.objects.other import RenderMaterial

import topologic
#--------------------------

#--------------------------
#DEFINITIONS
def createRandomChallenge(length=0):
    lowercase = list(string.ascii_lowercase)
    uppercase = list(string.ascii_uppercase)
    punctuation = ["-",".","_","~"] # Only hyphen, period, underscore, and tilde are allowed by OAuth Code Challenge
    digits = list(string.digits)
    masterlist = lowercase+uppercase+digits+punctuation
    masterlist = masterlist+lowercase+uppercase+digits
    random.shuffle(masterlist)
    if 0 < length <= 128:
        masterlist = random.sample(masterlist, random.randint(length, length))
    else:
        masterlist = random.sample(masterlist, random.randint(64, 128))
    return ''.join(masterlist)

def getStreams(client):
    return client.stream.list()
#--------------------------

#--------------------------
#PAGE CONFIG
st.set_page_config(
    page_title="Topologic Speckle Test Application",
    page_icon="📊",
    layout = "wide"
)
#--------------------------

#--------------------------
#CONTAINERS
header = st.container()
authenticate = st.container()
#--------------------------

#--------------------------
#HEADER
#Page Header
with header:
    st.title("Topologic Speckle Testing App📈")
#--------------------------

appID = st.secrets["appID"]
appSecret = st.secrets["appSecret"]

# This allows us to store variables locally
if 'challenge' not in st.session_state:
    st.session_state['challenge'] = None

challenge = st.session_state['challenge']
if not challenge:
    challenge = createRandomChallenge()
    st.session_state['challenge'] = None

if 'access_code' not in st.session_state:
    st.session_state['access_code'] = None
access_code = st.session_state['access_code']

if 'token' not in st.session_state:
    st.session_state['token'] = None
token = st.session_state['token']

if 'refresh_token' not in st.session_state:
    st.session_state['refresh_token'] = None
refresh_token = st.session_state['refresh_token']

if not access_code:
    # Verify the app with the challenge
    st.write("Verifying the App with the challenge string")
    verify_url="https://speckle.xyz/authn/verify/"+appID+"/"+challenge
    st.write("Click this to Verify:", verify_url)
else:
    st.write('Found challenge string stored locally: ', challenge)
    st.write('Found access code stored locally: ', access_code)
    st.write("Attempting to get token from access code and challenge")
    if not token or not refreshToken:
        tokens = requests.post(
                url=f"https://speckle.xyz/auth/token",
                json={
                    "appSecret": appSecret,
                    "appId": appID,
                    "accessCode": access_code,
                    "challenge": challenge,
                },
            )
        token = tokens.json()['token']
        refresh_token = tokens.json()['refreshToken']
        st.session_state['token'] = token
        st.session_state['refresh_token'] = refresh_token
    st.write('TOKEN: ', token)
    if token:
        account = get_account_from_token("speckle.xyz", token)
        st.write("ACCOUNT", account)
        client = SpeckleClient(host="speckle.xyz")
        client.authenticate_with_token(token)
        try:
            streams = getStreams(client)
        except:
            account = get_account_from_token("speckle.xyz", refresh_token)
            st.write("ACCOUNT", account)
            client = SpeckleClient(host="speckle.xyz")
            client.authenticate_with_token(refresh_token)
            streams = getStreams(client)
        stream_names = ["Select a stream"]
        for aStream in streams:
            stream_names.append(aStream.name)
        option = st.selectbox(
            'Select A Stream',
            (stream_names))
        if option != "Select a stream":
            stream = streams[stream_names.index(option)-1]
            st.write(option)
            st.subheader("Preview Image")
            st.components.v1.iframe(src="https://speckle.xyz/preview/"+stream.id, width=250,height=250)
            st.components.v1.iframe(src="https://speckle.xyz/embed?stream="+stream.id+"&transparent=false", width=400,height=600)
    else:
        st.write("Process Failed. Could not get account")
