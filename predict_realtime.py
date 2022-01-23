#Import Requires Libraries

import os
import cv2
import time
import joblib
import numpy as np
from keras.layers import Input, LSTM, Dense
from keras.models import Model, load_model
import extract_features
import config


class VideoDescriptionRealTime(object):
    """
        Initialize the parameters for the model
        """
    def __init__(self, config):
        self.latent_dim = config.latent_dim #the number of hidden features for lstm
        self.num_encoder_tokens = config.num_encoder_tokens #is the number of features from each frame
        self.num_decoder_tokens = config.num_decoder_tokens
        self.time_steps_encoder = config.time_steps_encoder
        self.max_probability = config.max_probability

        # models
        self.encoder_model = None
        self.decoder_model = None
        self.inf_encoder_model = None
        self.inf_decoder_model = None
        self.save_model_path = config.save_model_path
        self.test_path = config.test_path
        self.search_type = config.search_type #greedy search is used for vocab
        self.tokenizer = None
        self.num = 0

    def load_inference_models(self):
        # load model for futher process 

        with open(os.path.join(self.save_model_path, 'tokenizer' + str(self.num_decoder_tokens)), 'rb') as file:
            self.tokenizer = joblib.load(file)

        # inference encoder model
        self.inf_encoder_model = load_model(os.path.join(self.save_model_path, 'encoder_model.h5'))

        # inference decoder model
        decoder_inputs = Input(shape=(None, self.num_decoder_tokens))
        decoder_dense = Dense(self.num_decoder_tokens, activation='softmax') #check probability of last layer 
        decoder_lstm = LSTM(self.latent_dim, return_sequences=True, return_state=True)
        decoder_state_input_h = Input(shape=(self.latent_dim,))
        decoder_state_input_c = Input(shape=(self.latent_dim,))
        decoder_states_inputs = [decoder_state_input_h, decoder_state_input_c]
        decoder_outputs, state_h, state_c = decoder_lstm(decoder_inputs, initial_state=decoder_states_inputs)
        decoder_states = [state_h, state_c]
        decoder_outputs = decoder_dense(decoder_outputs)
        self.inf_decoder_model = Model(
            [decoder_inputs] + decoder_states_inputs,
            [decoder_outputs] + decoder_states)
        self.inf_decoder_model.load_weights(os.path.join(self.save_model_path, 'decoder_model_weights.h5'))

    def greedy_search(self, f):
        """

        :parameter f: the loaded numpy array after creating videos to frames and extracting features
        :return: the final sentence which has been predicted greedily
        """
        inv_map = self.index_to_word()
        states_value = self.inf_encoder_model.predict(f.reshape(-1, 80, 4096)) # 80 frames and 4096 featureof each frame fron vgg16 taken 
        target_seq = np.zeros((1, 1, 1500)) # 1500 is vocab world length 
        final_sentence = ''
        target_seq[0, 0, self.tokenizer.word_index['bos']] = 1 # begining of sentence 
        for i in range(15):
            output_tokens, h, c = self.inf_decoder_model.predict([target_seq] + states_value)
            states_value = [h, c]
            output_tokens = output_tokens.reshape(self.num_decoder_tokens)
            y_hat = np.argmax(output_tokens)
            if y_hat == 0:
                continue
            if inv_map[y_hat] is None:
                break
            if inv_map[y_hat] == 'eos': # End of sentence
                break
            else:
                final_sentence = final_sentence + inv_map[y_hat] + ' '
                target_seq = np.zeros((1, 1, 1500)) # 1*1 to 1500 words
                target_seq[0, 0, y_hat] = 1
        return final_sentence

    def decoded_sentence_tuning(self, decoded_sentence):
        # tuning sentence
        decode_str = []
        filter_string = ['bos', 'eos']
        uni_gram = {} # create empty dictionary
        last_string = ""
        for idx2, c in enumerate(decoded_sentence):
            if c in uni_gram:
                uni_gram[c] += 1
            else:
                uni_gram[c] = 1
            if last_string == c and idx2 > 0:
                continue
            if c in filter_string:
                continue
            if len(c) > 0:
                decode_str.append(c)
            if idx2 > 0:
                last_string = c
        return decode_str

    def index_to_word(self):
        # inverts word tokenizer
        index_to_word = {value: key for key, value in self.tokenizer.word_index.items()}
        return index_to_word

    def get_test_data(self):
        # loads the features array
        file_list = os.listdir(os.path.join(self.test_path, 'video'))
        
        file_name = file_list[self.num]
        path = os.path.join(self.test_path, 'feat', file_name + '.npy')
        if os.path.exists(path):
            f = np.load(path)
        else:
            model = extract_features.model_cnn_load()
            f = extract_features.extract_features(file_name, model)
        if self.num < len(file_list):
            self.num += 1
        else:
            self.num = 0
        return f, file_name

    def test(self):
        X_test, filename = self.get_test_data()
        # generate inference test outputs
        if self.search_type == 'greedy':
            sentence_predicted = self.greedy_search(X_test.reshape((-1, 80, 4096)))
        else:
            sentence_predicted = ''
            decoded_sentence = self.decode_sequence2bs(X_test.reshape((-1, 80, 4096)))
            decode_str = self.decoded_sentence_tuning(decoded_sentence)
            for d in decode_str:
                sentence_predicted = sentence_predicted + d + ' '
        # re-init max prob
        self.max_probability = -1
        return sentence_predicted, filename

    def main(self, filename, caption):
        """

        :param filename: the video to load
        :param caption: final caption
        :return:
        """
        # 1. Initialize reading video object
        cap1 = cv2.VideoCapture(os.path.join(self.test_path, 'video', filename))
        cap2 = cv2.VideoCapture(os.path.join(self.test_path, 'video', filename))
        caption = '[' + ' '.join(caption.split()[1:]) + ']'
        # 2. Cycle through pictures
        while cap1.isOpened():
            ret, frame = cap2.read()
            ret2, frame2 = cap1.read()
            if ret:
                imS = cv2.resize(frame, (480, 300))
                cv2.putText(imS, caption, (100, 270), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255),
                            2, cv2.LINE_4) # For font and colur of text on video
                cv2.imshow("VIDEO CAPTIONING", imS)
            if ret2:
                imS = cv2.resize(frame, (480, 300))
                cv2.imshow("ORIGINAL", imS)
            else:
                break

            # Quit playing
            key = cv2.waitKey(25)
            if key == 27:  # Button esc
                break

        # 3. Free resources
        cap1.release()
        cap2.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    video_to_text = VideoDescriptionRealTime(config)
    video_to_text.load_inference_models()
    while True:
        print('.........................\nGenerating Caption:\n')
        start = time.time()
        video_caption, file = video_to_text.test()
        end = time.time()
        sentence = ''
        print(sentence)
        for text in video_caption.split():
            sentence = sentence + ' ' + text
            print('\n.........................\n')
            print(sentence)
        print('\n.........................\n')
        print('It took {:.2f} seconds to generate caption'.format(end-start))
        video_to_text.main(file, sentence)
        play_video = input('Should I play the video? ')
        if play_video.lower() == 'y':
            continue
        elif play_video.lower() == 'n':
            break
        else:
            print('Could not understand type (y) for yes and (n) for no')
            continue