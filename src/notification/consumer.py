import pika
import sys
import os
from send import email

def main():
    try:
        credentials = pika.PlainCredentials('guest', 'guest')
        rabbitmq_host = os.getenv('RABBITMQ_SERVICE_HOST')
        print(rabbitmq_host)
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=rabbitmq_host, port=5672, credentials=credentials, heartbeat=600)  # Added heartbeat
        )
        channel = connection.channel()
        print("Connected to RabbitMQ successfully!")
    except Exception as e:
        print(f"Failed to connect to RabbitMQ: {e}")
        return
    
    def callback(ch, method, properties, body):
        err = email.notification(body)
        if err:
            print(f"Error sending email: {err}")
            ch.basic_nack(delivery_tag=method.delivery_tag)
        else:
            ch.basic_ack(delivery_tag=method.delivery_tag)

    queue_name = os.getenv("MP3_QUEUE", "mp3")
    print(f"Waiting for messages from queue: {queue_name}")

    channel.queue_declare(queue=queue_name, durable=True)

    channel.basic_consume(queue=queue_name, on_message_callback=callback)
    channel.start_consuming()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
