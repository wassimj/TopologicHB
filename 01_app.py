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

from topologicpy import HBModelByTopology, TopologyAddApertures
import json

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
    page_icon="????",
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
    icon_column, title_column = st.columns([1,10], gap="small")
    with icon_column:
        st.image("https://topologic.app/wp-content/uploads/2018/10/Topologic-Logo-250x250.png",width=100)
    with title_column:
        st.title("Topologic <> Speckle Test App")
#--------------------------

appID = st.secrets["appID"]
appSecret = st.secrets["appSecret"]

if 'access_code' not in st.session_state:
    st.session_state['access_code'] = None
if 'token' not in st.session_state:
    st.session_state['token'] = None
if 'refresh_token' not in st.session_state:
    st.session_state['refresh_token'] = None
if 'Building' not in st.session_state:
    st.session_state['Building'] = None
if 'Apertures' not in st.session_state:
    st.session_state['Apertures'] = None
if 'Shading' not in st.session_state:
    st.session_state['Shading'] = None
if 'hbjson' not in st.session_state:
    st.session_state['hbjson'] = None
if 'daylight_job' not in st.session_state:
    st.session_state['daylight_job'] = None
if 'energyanalysis_job' not in st.session_state:
    st.session_state['energyanalysis_job'] = None
try:
     access_code = st.experimental_get_query_params()['access_code'][0]
     st.session_state['access_code'] = access_code
except:
    access_code = None
    st.session_state['access_code'] = None

token = st.session_state['token']
refresh_token = st.session_state['refresh_token']

if not refresh_token:
    if not access_code:
        # Verify the app with the challenge
        verify_url="https://speckle.xyz/authn/verify/"+appID+"/"+st.secrets["challenge"]
        st.image("https://speckle.systems/content/images/2021/02/logo_big.png",width=100)
        link = '[Login to Speckle]('+verify_url+')'
        st.subheader(link)
    else:
        response = requests.post(
                url=f"https://speckle.xyz/auth/token",
                json={
                    "appSecret": appSecret,
                    "appId": appID,
                    "accessCode": access_code,
                    "challenge": st.secrets["challenge"],
                },
            )
        if (response.status_code == 200):
            token = response.json()['token']
            refresh_token = response.json()['refreshToken']
            st.session_state['token'] = token
            st.session_state['refresh_token'] = refresh_token
        else:
            st.write("Error occurred : " ,response.status_code, response.text)

streams = None
if st.session_state['refresh_token']:
    account = get_account_from_token("speckle.xyz", token)
    client = SpeckleClient(host="speckle.xyz")
    client.authenticate_with_token(token)
    try:
        streams = getStreams(client)
    except:
        streams = None
    if not isinstance(streams, list):
        account = get_account_from_token("speckle.xyz", refresh_token)
        client = SpeckleClient(host="speckle.xyz")
        client.authenticate_with_token(refresh_token)
        try:
            streams = getStreams(client)
        except:
            streams = None
commit_type = "Building"
if isinstance(streams, list):
    if len(streams) > 0:
        type_names = ["Select a type", "Building", "Apertures", "Shading"]
        option = st.selectbox(
            'Select A Type',
            type_names)
        if option != "Select a type":
            commit_type = option
            stream_names = ["Select a stream"]
            for aStream in streams:
                stream_names.append(aStream.name)
            option = st.selectbox(
                'Select A Stream',
                (stream_names))
            if option != "Select a stream":
                stream = streams[stream_names.index(option)-1]

                branches = getBranches([client, stream])
                branch_names = ["Select a branch"]
                for aBranch in branches:
                    branch_names.append(aBranch.name)

                option = st.selectbox(
                    'Select A Branch',
                    (branch_names))
                if option != "Select a branch":
                    branch = branches[branch_names.index(option)-1]
                    
                    commits = getCommits(branch)
                    commit_names = ["Select a commit"]
                    for aCommit in commits:
                        commit_names.append(str(aCommit.id)+": "+aCommit.message)
                    option = st.selectbox('Select A Commit', (commit_names))
                    if option != "Select a commit":
                        commit = commits[commit_names.index(option)-1]
                        st.components.v1.iframe(src="https://speckle.xyz/embed?stream="+stream.id+"&commit="+commit.id+"&transparent=false", width=600,height=400)
        
                        last_obj = getObject(client, stream, commit)
                        st.write(last_obj)
                        sp_vertices = last_obj.vertices
                        sp_faces = last_obj.faces
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
                        if len(tp_faces) == 1:
                            tp_object = tp_faces[0]
                        else:
                            tp_object = cellComplexByFaces([tp_faces, 0.0001])
                            if not tp_object:
                                tp_object = cellByFaces([tp_faces, 0.0001])
                            if not tp_object:
                                tp_object = shellByFaces([tp_faces, 0.0001])
                            if not tp_object:
                                tp_object = topologic.Cluster.ByTopologies(tp_faces)
                        st.session_state[commit_type] = tp_object
                        
building = st.session_state['Building']
apertureCluster = st.session_state['Apertures']
shadingCluster = st.session_state['Shading']

if building and apertureCluster and isinstance(building, topologic.CellComplex) and isinstance(apertureCluster, topologic.Cluster):
    new_building = TopologyAddApertures.processItem([building, apertureCluster, True, 0.0001, "Face"])
    st.write("New Building:", new_building)
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
        st.session_state['hbjson'] = hbjson_string
        st.write("DONE, you can now go on to the next page")








            
