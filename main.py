from flask import Flask, render_template, request, redirect
from google.auth.transport import requests
import google.oauth2.id_token
from datetime import datetime
import random
from google.cloud import datastore
from models import Gpu
import datetime

app = Flask(__name__)
datastore_client = datastore.Client()
firebase_request_adapter = requests.Request()

BOOLEAN_KEY_LIST = [
    "sparseBinding",
    "shaderInt16",
    "geometryShader",
    "tesselationShader",
    "textureCompressionETC2",
    "vertexPipelineStoresAndAtomics",
]

def checkUserData():
    id_token = request.cookies.get("token")
    error_message = None
    claims = None
    user_info = None
    addresses = None
    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token,firebase_request_adapter)
        except ValueError as exc:
            error_message = str(exc)
    return claims

def getgpudata():
    gpu_data = []
    query = datastore_client.query(kind="GpuInfo")
    query = query.fetch()
    for i in query:
        data = dict(i)
        data["name"] = i.key.name
        gpu_data.append(data)
    return gpu_data

def getgpudetails(name):
    entity_key = datastore_client.key("GpuInfo", name)
    enitity_exists = datastore_client.get(key=entity_key)
    if enitity_exists:
        enitity_exists = dict(enitity_exists)
        enitity_exists["name"] = name
    else:
        return render_template("error.html", error_message="No data found")
    return enitity_exists

#root function is a default function
@app.route('/')
def root():
    user_data =checkUserData();
    if user_data == None:
        error_message = "Page not loaded! User Data is missing"
        return render_template("index.html", user_data=user_data, error_message=error_message)
    else:
        return render_template("main.html", user_data=user_data)

#create gpu entry
@app.route("/gpucreate", methods=["GET", "POST"])
def gpudatacreate():
    user_data =checkUserData()
    if user_data != None:
        data = dict(request.form)

        name = data.get("name")
        if name:
            entity_key = datastore_client.key("GpuInfo", name)
            enitity_exists = datastore_client.get(key=entity_key)
            if not enitity_exists:
                #create the gpu if an entry with name not exists
                entity = datastore.Entity(key=entity_key)
                data.pop("name")
                gpu = Gpu(name= name, doi = data.get("doi"), manufacturer=data.get("manufacturer"))
                for key in BOOLEAN_KEY_LIST:
                    if key in data:
                        gpu.set_properties(key, True)
                    else:
                        gpu.set_properties(key, False)
                gpu.set_properties('createdBy', user_data['email'])
                gpu.set_properties('createdDate', datetime.datetime.now())
                entity.update(gpu.__dict__)
                datastore_client.put(entity)
            else:
                error_message = "an entry with same name already exists. try with an another name"
                return render_template("error.html", error_message=error_message)
        return render_template("gpucreate.html", user_data=user_data)
    else:
        error_message = "Page is not loaded! User Data is missing"
        return render_template("index.html", user_data=user_data, error_message=error_message)

@app.route("/gpulist", methods=["GET", "POST"])
def allgpulist():
    user_data =checkUserData();
    if user_data == None:
        error_message = "Page not loaded! User Data is missing"
        return render_template("index.html", user_data=user_data, error_message=error_message)
    else:
        try:
            gpu_data = getgpudata()
            return render_template("gpulist.html", user_data=user_data, gpu_list=gpu_data)
        except ValueError as exc:
            error_message = str(exc)
            return render_template("error.html", error_message=error_message)

@app.route("/gpudetails/<name>", methods=["GET", "POST"])
def gpudatadetails(name=None):
    user_data =checkUserData();
    if user_data != None:
        if name:
            enitity_exists = getgpudetails(name)
            if enitity_exists:
                return render_template("gpudetails.html", gpu_data=enitity_exists, user_data=user_data)
            else:
                return render_template("error.html", error_message="No data found")
    else:
        error_message = "Page is not loaded! User Data is missing"
        return render_template("index.html", user_data=user_data, error_message=error_message)


@app.route("/gpuedit/<name>", methods=["GET", "POST"])
def gpudataedit(name=None):
    user_data =checkUserData();
    if user_data != None:
        if name:
            entity_key = datastore_client.key("GpuInfo", name)
            enitity_exists = datastore_client.get(key=entity_key)
            if enitity_exists:
                enitity_exists = dict(enitity_exists)
                enitity_exists["name"] = name
                if request.method == "GET":
                    return render_template("gpuedit.html", gpu_data=enitity_exists, user_data=user_data)
                else:
                    try:
                        data = dict(request.form)
                        if(data.get("editedname") != data.get("oldname") ):
                            newentry_key = datastore_client.key("GpuInfo", data.get("editedname"))
                            newenitity_exists = datastore_client.get(key=newentry_key)
                            if newenitity_exists:
                                error_message = "An entry with same name already exists. try with an another name"
                                return render_template("error.html", error_message=error_message)
                        entity = datastore.Entity(key=entity_key)
                        gpu = Gpu(name=data.get("editedname"), doi=data.get("doi"), manufacturer=data.get("manufacturer"))
                        gpu.set_properties('createdBy', data.get('createdBy'))
                        cr_date =data.get('createdDate')
                        gpu.set_properties('createdDate', datetime.datetime.strptime(cr_date[:19], '%Y-%m-%d %H:%M:%S'))
                        gpu.set_properties('editedBy', user_data['email'])
                        gpu.set_properties('editedDate', datetime.datetime.now())
                        for key in BOOLEAN_KEY_LIST:
                            if key in data:
                                gpu.set_properties(key, True)
                            else:
                                gpu.set_properties(key, False)
                        obj = gpu.__dict__
                        obj.pop("name")
                        entity.update(obj)
                        datastore_client.put(entity)
                        enitity_exists = getgpudetails(data.get("editedname"))
                        if enitity_exists:
                            return render_template("gpudetails.html", gpu_data=enitity_exists, user_data=user_data)
                        else:
                            return render_template("error.html", error_message="No data found")
                    except Exception as e:
                        return render_template("error.html", error_message=str(e))
    else:
        error_message = "Page is not loaded! User Data is missing"
        return render_template("index.html", user_data=user_data, error_message=error_message)

@app.route("/gpusignout", methods=["GET", "POST"])
def gpusignout():
    return render_template("index.html", signoutdata="true")

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
