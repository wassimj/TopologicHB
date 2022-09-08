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

def to_argb_int(diffuse_color) -> int:
    """Converts an RGBA array to an ARGB integer"""
    diffuse_color = diffuse_color[-1:] + diffuse_color[:3]
    diffuse_color = [int(val * 255) for val in diffuse_color]
    return int.from_bytes(diffuse_color, byteorder="big", signed=True)

def to_speckle_material(diffuse_color) -> RenderMaterial:
    speckle_mat = RenderMaterial()
    speckle_mat.diffuse = to_argb_int(diffuse_color)
    speckle_mat.metalness = 0
    speckle_mat.roughness = 0
    speckle_mat.emissive = to_argb_int([0,0,0,1]) #black for emissive
    speckle_mat.opacity = diffuse_color[-1]
    return speckle_mat

def getBranches(item):
	client, stream = item
	bList = client.branch.list(stream.id)
	branches = []
	for b in bList:
		branches.append(client.branch.get(stream.id, b.name))
	return branches

def getStreams(client):
    return client.stream.list()

def getCommits(branch):
    return branch.commits.items

def getObject(client, stream, commit):
    transport = ServerTransport(stream.id, client)
    last_obj_id = commit.referencedObject
    return operations.receive(obj_id=last_obj_id, remote_transport=transport)

def cellComplexByFaces(item):
    faces, tol = item
    assert isinstance(faces, list), "CellComplex.ByFaces - Error: Input is not a list"
    faces = [x for x in faces if isinstance(x, topologic.Face)]
    cellComplex = topologic.CellComplex.ByFaces(faces, tol, False)
    if not cellComplex:
        return None
    cells = []
    _ = cellComplex.Cells(None, cells)
    if len(cells) < 2:
        return None
    return cellComplex

def cellByFaces(item):
    faces, tol = item
    return topologic.Cell.ByFaces(faces, tol)

def shellByFaces(item):
	faces, tol = item
	shell = topologic.Shell.ByFaces(faces, tol)
	if not shell:
		result = faces[0]
		remainder = faces[1:]
		cluster = topologic.Cluster.ByTopologies(remainder, False)
		result = result.Merge(cluster, False)
		if result.Type() != 16: #16 is the type of a Shell
			if result.Type() > 16:
				returnShells = []
				_ = result.Shells(None, returnShells)
				return returnShells
			else:
				return None
	else:
		return shell
    
def speckleMeshToTopologic(obj):
    sp_vertices = obj.vertices
    sp_faces = obj.faces
    tp_vertices = []
    for i in range(0,len(sp_vertices),3):
        x = sp_vertices[i]
        y = sp_vertices[i+1]
        z = sp_vertices[i+2]
        tp_vertices.append(topologic.Vertex.ByCoordinates(x,y,z))
    
    tp_faces = []
    i = 0
    while True:
        if sp_faces[i] == 0:
            n = 3
        else:
            n = 4
        temp_verts = []
        for j in range(n):
            temp_verts.append(tp_vertices[sp_faces[i+j+1]])
        c = topologic.Cluster.ByTopologies(temp_verts)
        w = wireByVertices([c, True])
        f = topologic.Face.ByExternalBoundary(w)
        tp_faces.append(f)
        i = i + n + 1
        if i+n+1 > len(sp_faces):
            break
    returnTopology = None
    try:
        returnTopology = cellComplexByFaces([tp_faces, 0.0001])
    except:
        try:
            returnTopology = cellByFaces([tp_faces, 0.0001])
        except:
            try:
                returnTopology = shellByFaces([tp_faces, 0.0001])
            except:
                returnTopology = topologic.Cluster.ByTopologies(tp_faces)
    return returnTopology

def wireByVertices(item):
	cluster, close = item
	if isinstance(close, list):
		close = close[0]
	if isinstance(cluster, list):
		if all([isinstance(item, topologic.Vertex) for item in cluster]):
			vertices = cluster
	elif isinstance(cluster, topologic.Cluster):
		vertices = []
		_ = cluster.Vertices(None, vertices)
	else:
		raise Exception("WireByVertices - Error: The input is not valid")
	wire = None
	edges = []
	for i in range(len(vertices)-1):
		v1 = vertices[i]
		v2 = vertices[i+1]
		try:
			e = topologic.Edge.ByStartVertexEndVertex(v1, v2)
			if e:
				edges.append(e)
		except:
			continue
	if close:
		v1 = vertices[-1]
		v2 = vertices[0]
		try:
			e = topologic.Edge.ByStartVertexEndVertex(v1, v2)
			if e:
				edges.append(e)
		except:
			pass
	if len(edges) > 0:
		c = topologic.Cluster.ByTopologies(edges, False)
		return c.SelfMerge()
	else:
		return None

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

st.write("Challenge:", challenge)
if 'access_code' not in st.session_state:
    st.session_state['access_code'] = None
access_code = st.session_state['access_code']

st.write("Access Code:", access_code)
if 'token' not in st.session_state:
    st.session_state['token'] = None
token = st.session_state['token']

if 'refresh_token' not in st.session_state:
    st.session_state['refresh_token'] = None
refresh_token = st.session_state['refresh_token']

st.write("Debugging Access Code:", st.experimental_get_query_params()['access_code'][0])
try:
     access_code = st.experimental_get_query_params()['access_code'][0]
     st.session_state['access_code'] = access_code
except:
    access_code = None

if not access_code:
    # Verify the app with the challenge
    st.write("Verifying the App with the challenge string")
    verify_url="https://speckle.xyz/authn/verify/"+appID+"/"+challenge
    st.write("Click this to Verify:", verify_url)
else:
    st.write('Found challenge string stored locally: ', challenge)
    st.write('Found access code stored locally: ', access_code)
    st.write("Attempting to get token from access code and challenge")
    if not token or not refresh_token:
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