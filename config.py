#Configuaration for project  

train_path = "data/training_data"
test_path = "data/testing_data"
batch_size = 320
learning_rate = 0.0007
epochs = 150
latent_dim = 512
num_encoder_tokens = 4096 #feature per frame 
num_decoder_tokens = 1500 # length of vocab
time_steps_encoder = 80
max_probability = -1
save_model_path = 'model_final'
validation_split = 0.15
max_length = 10  #LSTM cell
search_type = 'greedy'