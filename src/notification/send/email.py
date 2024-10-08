import smtplib,os,json
from email.message import EmailMessage

def notification(message):  
    try:
        message=json.loads(message)
        print("message ",message)
        mp3_fid=message["mp3_fid"]
        sender_address= os.environ.get("GMAIL_ADDRESS")
        sender_password= os.environ.get("GMAIL_PASSWORD")
        receiver_adderss= message["username"]

        msg=EmailMessage()
        msg.set_content(f"mp3 file_id: {mp3_fid} is now ready!")
        msg['Subject']="MP3 Download"
        msg["From"]=sender_address
        msg["To"]=receiver_adderss
        session = smtplib.SMTP('smtp.gmail.com', 587)
        session.starttls()
        session.login(sender_address,sender_password)
        session.send_message(msg,sender_address,receiver_adderss)
        session.quit()
        print("Successfully Sent the Email!")
    except Exception as err:
        print(err)
        return err