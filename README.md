# Video-Captioning

Video Captioning is an encoder decoder mode based on sequence to sequence learning.
It takes a video as input and generates a caption describing the event in the video. 

The importance of captioning lies in its ability to make video more accessible in numerous ways. 
Automated video caption generator helps searching of videos in websites better. 
It can be used for clustering of videos based on their content easier.

## Table of contents
* <a href="#Setup">Setup</a>
* <a href="#Usage">Usage</a>
* <a href="#Features">Features</a>
* <a href="#FutureDevelopment">Future Development</a>


<h2 id="Setup">Setup</h2>
Clone the repository : <code>git clone https://github.com/saavn03/Major-Project-Video-Captioning.git</code>

Video Caption Generator: <code>cd Major-Project-Video-Captioning</code>

Create environment: <code>conda create -n video_caption python=3.7</code>

Activate environment: <code>conda activate video_caption</code>

Install requirements: <code>pip install -r requirements.txt</code>

<h2 id="Usage">Usage</h2>
To use the models that have already been trained

Add a video to **data/testing_data/video** folder and run the predict realtime file as <code>python predict_realtime.py</code>

For faster results extract the features of the video and save it in feat folder of the testing_data.

To convert into features run the extract_features.py file as <code>python extract_features.py</code>
 


<h2 id="Features">Features</h2>
<ul>
 <li> Realtime implementation</li>
 <li> Short video captioning</li>
 <li> Greedy search</li>
 </ul>
 
Greedy search selects the most likely word at each step in the output sequence.
To get more information on greedy search algorithms check out this <a href="https://machinelearningmastery.com/beam-search-decoder-natural-language-processing/">post</a> 

 <h2 id="Scripts">Scripts</h2>
 
 * **train.py** contains the model architecture
 * **predict_test.py** is to check for predicted results and store them in a txt file along with the time taken for each prediction
 * **predict_realtime.py** checks the results in realtime
 * **model_final** folder contains the trained encoder model along with the tokenizerl and decoder model weights.
 *  It extracts 80 frames evenly spread from the video and then those video frames are processed by a pre-trained VGG16 so each frame
    has 4096 dimensions. So for a video we create a numoy array of shape(80, 4096)
    config.py contains all the configurations thats used in this project.


<h2 id="FutureDevelopment">Future Development</h2>
<ul>
 <li> Adding attention blocks and pretrained embeddding like glove so that the model understands sentences better</li> 
 <li> Using other pretrained models to extract features specially ones made for understanding videos like I3D</li> 
 <li> Right now the model uses only 80 frames improvements need to be made so that it can work even for longer videos</li>
 <li> Adding a UI to the project</li>
</ul>

