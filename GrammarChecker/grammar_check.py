# First uninstall Keras, then install nmt-keras
import tensorflow as tf
import os
from config import load_parameters
from nmt_keras.model_zoo import TranslationModel
from keras_wrapper.cnn_model import loadModel, updateModel
from keras_wrapper.dataset import loadDataset
from keras_wrapper.extra.callbacks import PrintPerformanceMetricOnEpochEndOrEachNUpdates
from keras_wrapper.utils import decode_predictions_beam_search
from keras_wrapper.extra.read_write import list2file

epoch_num = 3

class GrammarChecker:
    def __init__(self):
        self.session = tf.Session()
        self.graph = tf.get_default_graph()
        with self.graph.as_default():
            with self.session.as_default():
                dataset = loadDataset("dataset/Dataset_tutorial_dataset.pkl")
                nmt_model = loadModel("model", epoch_num)
                params = nmt_model.params
                inputMapping = dict() 
                for i, id_in in enumerate(params['INPUTS_IDS_DATASET']): 
                    pos_source = dataset.ids_inputs.index(id_in) 
                    id_dest = nmt_model.ids_inputs[i] 
                    inputMapping[id_dest] = pos_source 
                nmt_model.setInputsMapping(inputMapping) 

                outputMapping = dict() 
                for i, id_out in enumerate(params['OUTPUTS_IDS_DATASET']): 
                    pos_target = dataset.ids_outputs.index(id_out) 
                    id_dest = nmt_model.ids_outputs[i] 
                    outputMapping[id_dest] = pos_target 
                nmt_model.setOutputsMapping(outputMapping)
                params_prediction = {
                    'language': 'en',
                    'tokenize_f': eval('dataset.' + 'tokenize_basic'),
                    'beam_size': 2,
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
                    'length_norm_factor': 1.0,
                    'length_penalty': True,
                    'predict_on_sets': ['test'],
                    'verbose': 0,
                  }
                self.params = params
                self.dataset = dataset
                self.nmt_model = nmt_model
                self.params_prediction = params_prediction

    def check_grammar(self, input_sentence):

        with self.graph.as_default():
            with self.session.as_default():
                user_input = input_sentence
                with open('user_input.txt', 'w') as f:
                    f.write(user_input)
                self.dataset.setInput('user_input.txt',
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

                self.dataset.setRawInput('user_input.txt',
                              'test',
                              type='file-name',
                              id='raw_source_text',
                              overwrite_split=True)

                
                vocab = self.dataset.vocabulary['target_text']['idx2words']

                predictions = self.nmt_model.predictBeamSearchNet(self.dataset, self.params_prediction)['test']
                if self.params_prediction['pos_unk']:
                    samples = predictions['samples']
                    alphas = predictions['alphas']
                else:
                    samples = predictions
                    heuristic = None
                    sources = None
                predictions = decode_predictions_beam_search(samples,  # The first element of predictions contain the word indices.
                                                         vocab,
                                                         verbose=self.params['VERBOSE'])
            
                #print("Correct Prediction: {}".format(predictions[0]))
                return predictions[0]
