import os
from decouple import config
from flask import (
    Flask, request, abort
)
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

import psycopg2
DSN = "postgres://postgres:root@localhost:5432/skripsweet"
import datetime

# import sys
# sys.path.append("/root/skripsweet_adminpybot")

# from django.conf import settings

# settings.configure()

# from skripsweet_adminpage.models import *

from rasa_core.agent import Agent
from rasa_nlu.model import Trainer, Metadata
from rasa_core.interpreter import RasaNLUInterpreter
from rasa_core.utils import EndpointConfig

nlu_interpreter = RasaNLUInterpreter('models/nlu/default/chat')
action_endpoint = EndpointConfig(url="http://localhost:5055/webhook")
agent = Agent.load('./models/dialogue', interpreter=nlu_interpreter, action_endpoint = action_endpoint)


app = Flask(__name__)
# get LINE_CHANNEL_ACCESS_TOKEN from your environment variable
line_bot_api = LineBotApi(
    config("LINE_CHANNEL_ACCESS_TOKEN",
           default=os.environ.get('LINE_ACCESS_TOKEN'))
)
# get LINE_CHANNEL_SECRET from your environment variable
handler = WebhookHandler(
    config("LINE_CHANNEL_SECRET",
           default=os.environ.get('LINE_CHANNEL_SECRET'))
)


@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']


    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)


    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    profile = line_bot_api.get_profile(event.source.user_id)
    print(profile.display_name)
    print(event.message.text)
    timestamp = datetime.datetime.now()
    user_message = event.message.text
    responses=agent.handle_message(user_message)
    message_res = []
    for response in responses:
        print(response)
        if response['text'] == 'Maaf untuk saat ini, sistem tidak memahami maksud kakak. Mohon tunggu karena pesan akan diteruskan kepada admin untuk ditanggapi.':
            with psycopg2.connect(DSN) as conn:
                with conn.cursor() as curs:
                    curs.execute(f"""SELECT MAX(idchat) FROM skripsweet_adminpage_chat """)
                    idchat_res = curs.fetchone() 
                    idchat = int(idchat_res[0]) + 1
                    curs.execute(f"""SELECT idchatroom FROM skripsweet_adminpage_chatroom WHERE profilename LIKE '{profile.display_name}' """)
                    idchatroom = curs.fetchone()  
                    if idchatroom is None:
                        curs.execute(f"""SELECT MAX(idchatroom) FROM skripsweet_adminpage_chatroom """)
                        idchatroom_res = curs.fetchone() 
                        idchatroom = int(idchatroom_res[0]) + 1
                        curs.execute("INSERT INTO skripsweet_adminpage_chatroom (idchatroom,profilename) VALUES (%s,%s)",(idchatroom,profile.display_name))
                    curs.execute("INSERT INTO skripsweet_adminpage_chat (idchat,message,timestamp,status) VALUES (%s,%s,%s,%s)",(idchat,user_message,timestamp,'0'))
                    curs.execute("INSERT INTO skripsweet_adminpage_chathistory (idchatroom_id,idchat_id) VALUES (%s,%s)",(idchatroom,idchat))
        message_res.append(response['text'])
    message_res = "\n".join(message_res)
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=message_res)
    )



if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)