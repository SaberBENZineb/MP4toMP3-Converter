import os, gridfs, pika, json
from flask import Flask, request, send_file
from flask_pymongo import PyMongo
from auth import validate
from auth_svc import access
from storage import util
from bson.objectid import ObjectId

server=Flask(__name__)

MONGO_URI= os.environ.get("MONGO_URI_VIDEO")
mongoVideos = PyMongo(server,f'{MONGO_URI}/videos')
fsVideos = gridfs.GridFS(mongoVideos.db)

mongoMp3s = PyMongo(server,f'{MONGO_URI}/mp3s')
fsMp3 = gridfs.GridFS(mongoMp3s.db)

try:
    mongoVideos.db.command("ping")
    print("MongoDB connection is alive!")
except Exception as e:
    print(f"Failed to ping MongoDB: {e}")

try:
    credentials = pika.PlainCredentials('guest', 'guest')
    rabbitmq_host = os.getenv('RABBITMQ_SERVICE_HOST')
    print(rabbitmq_host)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=rabbitmq_host, port=5672, credentials=credentials)
    )
    channel = connection.channel()
    print("Connected to RabbitMQ successfully!")
except Exception as e:
    print(f"Failed to connect to RabbitMQ: {e}")

@server.route("/login",methods=["POST"])
def login():
    token, err=access.login(request)

    if not err:
        return token
    else:
        return err
    
@server.route("/upload",methods=["POST"])
def upload():
    access, err=validate.token(request)

    if err:
        return err

    access=json.loads(access)

    if access["admin"]:
        if len(request.files) != 1 :
            return "exactly 1 file required", 400
        
        for _,f in request.files.items():
            err= util.upload(f,fsVideos,channel,access)
            if err:
                return err
            
        return "success!", 200
    else:
        return "not authorized", 401
    
@server.route("/download",methods=["GET"])
def download():
    access, err=validate.token(request)

    if err:
        return err

    access=json.loads(access)

    if access["admin"]:
        fid_string = request.args.get("fid")  
        if not fid_string:
            return "fid is required", 400  

        try:
            out = fsMp3.get(ObjectId(fid_string))
            return send_file(out,download_name=f'{fid_string}.mp3')
        except Exception as err:
            print(err)
            return "internal server error", 500
    else:
        return "not authorized", 401


if __name__=="__main__":
    server.run(host="0.0.0.0",port=8080)
    
