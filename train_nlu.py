from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

# Imports
#-----------
# rasa nlu
from rasa_nlu.training_data import load_data
from rasa_nlu.config import RasaNLUModelConfig
from rasa_nlu.model import Trainer
from rasa_nlu.model import Metadata, Interpreter
from rasa_nlu import config

# Functions
#------------
def train (data, config_file, model_dir):
    training_data = load_data(data)
    configuration = config.load(config_file)
    trainer = Trainer(configuration)
    trainer.train(training_data)
    model_directory = trainer.persist(model_dir, fixed_model_name = 'chat')

def run():
    interpreter = Interpreter.load('./models/nlu/default/chat')
    print(interpreter.parse('hi sis'))
    print(interpreter.parse('misi sis'))
    print(interpreter.parse('ada case oppo a37s ?'))
    print(interpreter.parse('halo sis'))
    print(interpreter.parse('halo kak'))
    print(interpreter.parse('saya mau tanya custom case samsung s7 ada ?'))
    print(interpreter.parse('kak apa ada custom case iphone 7?'))
# Training
#------------
if __name__ == '__main__':
    train('data/testData.md', 'config/nlu_config.yml', 'models/nlu')
    run()
