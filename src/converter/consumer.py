import pika,sys,os,time
from pymongo import MongoClient
import gridfs
from convert import to_mp3

def main():
    MONGO_URI= os.environ.get("MONGO_URI")
    client=MongoClient(MONGO_URI,27017)
    dv_videos=client.videos
    db_mp3s=client.mp3s
    
    #gridfs
    fs_videos=gridfs.GridFS(dv_videos)
    fs_mp3s=gridfs.GridFS(db_mp3s)

    #rabbitmq connection
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
    def callback(ch,method,properties,body):
        err=to_mp3.start(body,fs_videos,fs_mp3s,ch)
        if err:
            ch.basic_nack(delivery_tag=method.delivery_tag)
        else:
            ch.basic_ack(delivery_tag=method.delivery_tag)
    try:
        channel.basic_consume(queue=os.environ.get("VIDEO_QUEUE"),on_message_callback=callback)
        print("Waiting for messages. To exit press CTRL+C")
        channel.start_consuming()
    except KeyboardInterrupt:
        print("Interrupted by user, stopping consumer...")
        channel.stop_consuming()
    finally:
        if connection:
            connection.close()

if __name__=="__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
