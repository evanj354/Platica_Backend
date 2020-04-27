from keras_wrapper.dataset import loadDataset
from keras_wrapper.cnn_model import loadModel
from keras_wrapper.utils import decode_predictions_beam_search
# from config import load_parameters
from keras_wrapper.extra.read_write import list2file
import os

MODEL_PATH = os.path.join(os.getcwd(), 'Chatbot/models/persona_chat_lstm')
epoch_choice = 5

class Chatbot:
    def __init__(self):
        print('Initializing Chatbot...')
        dataset = loadDataset(os.path.join(MODEL_PATH, "dataset/Dataset_tutorial_dataset.pkl"))
        nmt_model = loadModel(MODEL_PATH, epoch_choice)
        params = nmt_model.params
        print('input vocab size:' + str(params['INPUT_VOCABULARY_SIZE']))
        print('output vocab size:' + str(params['OUTPUT_VOCABULARY_SIZE']))
        # 17819
        params_prediction = {
            'language': 'en',
            'tokenize_f': eval('dataset.' + 'tokenize_basic'),
            'beam_size': 6,
            'optimized_search': True,
            'model_inputs': params['INPUTS_IDS_MODEL'],
            'model_outputs': params['OUTPUTS_IDS_MODEL'],
            'dataset_inputs':  params['INPUTS_IDS_DATASET'],
            'dataset_outputs':  params['OUTPUTS_IDS_DATASET'],
            'n_parallel_loaders': 1,
            'maxlen': 50,
            'model_inputs': ['source_text', 'state_below'],
            'model_outputs': ['target_text'],
            'dataset_inputs': ['source_text', 'state_below'],
            'dataset_outputs': ['target_text'],
            'normalize': True,
            'pos_unk': True,
            'heuristic': 0,
            'state_below_maxlen': -1,
            'predict_on_sets': ['test'],
            'verbose': 0,
          }
        self.dataset = dataset
        self.model = nmt_model
        self.params = params_prediction
        print('Model initialized')

    def predictResponse(self, context):
        with open(os.path.join(MODEL_PATH, 'context.txt'), 'w') as f:
            f.write(context)
        self.dataset.setInput(os.path.join(MODEL_PATH, 'context.txt'),
            'test',
            type='text',
            id='source_text',
            pad_on_batch=True,
            tokenization='tokenize_basic',
            fill='end',
            max_text_len=30,
            min_occ=0,
            overwrite_split=True)

        self.dataset.setInput(None,
                    'test',
                    type='ghost',
                    id='state_below',
                    required=False,
                    overwrite_split=True)

        self.dataset.setRawInput(os.path.join(MODEL_PATH, 'context.txt'),
                      'test',
                      type='file-name',
                      id='raw_source_text',
                      overwrite_split=True)
        
        vocab = self.dataset.vocabulary['target_text']['idx2words']
        predictions = self.model.predictBeamSearchNet(self.dataset, self.params)['test']

        if self.params['pos_unk']:
            samples = predictions['samples']
            alphas = predictions['alphas']
        else:
            samples = predictions
            heuristic = None
            sources = None

        predictions = decode_predictions_beam_search(samples, vocab)
        return predictions[0]
