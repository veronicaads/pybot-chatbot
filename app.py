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
    print(event.message.text)
    user_message = event.message.text
    responses=agent.handle_message(user_message)
    message_res = []
    for response in responses:
        print(response)
        # if response['text'] == 'Maaf untuk saat ini, sistem tidak memahami maksud kakak. Mohon tunggu karena pesan akan diteruskan kepada admin untuk ditanggapi.':
        #     print('Masuk')
        #     cr = Chatroom()
        #     cr.idchatroom = str(int(1 if Chatroom.objects.all().last() == None else Chatroom.objects.all().last().idchatroom) + 1)
        #     cr.profilename = profile.user_id
        #     cr.save()
        #     ch = Chat()
        #     ch.idchat = str(int(1 if Chat.objects.all().last() == None else Chat.objects.all().last().idchat) + 1)
        #     ch.message = user_message
        #     ch.timestamp = str(datetime.datetime.now()).split()
        #     ch.status = 0
        #     ch.save()
        #     chis = ChatHistory()
        #     chis.idchat = ch.idchat
        #     chis.idchatroom = ch.idchatroom
        #     chis.save()  
        message_res.append(response['text'])
    message_res = "\n".join(message_res)
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=message_res)
    )



if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)