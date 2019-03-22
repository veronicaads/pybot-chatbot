from rasa_core.agent import Agent
from rasa_nlu.model import Trainer, Metadata
from rasa_core.interpreter import RasaNLUInterpreter
from rasa_core.utils import EndpointConfig

nlu_interpreter = RasaNLUInterpreter('models/nlu/default/chat')
action_endpoint = EndpointConfig(url="http://localhost:5055/webhook")
agent = Agent.load('./models/dialogue', interpreter=nlu_interpreter, action_endpoint = action_endpoint)


# # Part 4:Talk to Bot

#from clint.textui import colored, puts 
print("start the conversation")
print()
print("Hi! How Can I help you today?")
while True:
    a=input()
    if a == 'stop' :
        break
    responses=agent.handle_message(a)
    for response in responses:
        print(response['text'])