from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import logging
import tensorflow
import rasa_core
from rasa_core.agent import Agent
from rasa_core.policies import FallbackPolicy, KerasPolicy, MemoizationPolicy
from rasa_core.interpreter import RasaNLUInterpreter
from rasa_core.run import serve_application
from rasa_core.utils import EndpointConfig

logger = logging.getLogger(__name__)


def train_dialogue(domain_file = './domain/domain.yml',
					model_path = './models/dialogue',
					training_data_file = './data/stories.md'):
	fallback = FallbackPolicy(fallback_action_name="utter_unclear",core_threshold=0.2, nlu_threshold=0.65)
	agent = Agent(domain_file , policies=[MemoizationPolicy(max_history=10), KerasPolicy(), fallback])
	data = agent.load_data(training_data_file)
	agent.train(data)
	agent.persist(model_path)
	return agent
	
def run_dialogue(serve_forever=True):
	interpreter = RasaNLUInterpreter('./models/nlu/default/chatter')
	action_endpoint = EndpointConfig(url="http://localhost:5055/webhook")
	agent = Agent.load('./models/dialogue', interpreter=interpreter, action_endpoint=action_endpoint)
	rasa_core.run.serve_application(agent ,channel='cmdline')
	return agent
	
if __name__ == '__main__':
	train_dialogue()