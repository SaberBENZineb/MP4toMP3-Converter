import pika,json

def upload(f,fs,channel,access):
    try:
        fid = fs.put(f)
        print(f"File uploaded to GridFS with id: {fid}")
    except Exception as err:
        print(f"Error uploading file to GridFS: {err}")
        return "GridFS internal server error ", 500
    
    message={
        "video_fid":str(fid),
        "mp3_fid":None,
        "username": access["username"],
    }
    try:
        channel.basic_publish(
            exchange="",
            routing_key="video",
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            )
        )
        print("message sended!")
    except:
        fs.delete(fid)
        return "send message internal server error",500
