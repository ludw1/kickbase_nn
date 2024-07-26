# Overview
Project to use a neural net, more specifically the Transformers architecture, to predict marketvalues of players on the popular football fantasy manager [kickbase.com](https://www.kickbase.com). Using a [N-HiTS model](https://unit8co.github.io/darts/generated_api/darts.models.forecasting.nhits.html) and the [Darts python package](https://unit8co.github.io/darts/index.html) the player data is converted into a time series and subsequently fed into the neural net. Using the kickbase bot, the predictions can now be leveraged to automatically place offers on players if they fulfill certain criteria (expiry not too close or too far away, market value threshold, rising trend etc.). The kickbase bot also claims the bonus every day.
## Usage
1. Install the necessary packages using ```pip install -r requirements.txt```
2. Download pretrained model files from [here](https://drive.google.com/drive/folders/1D0JoHirmZWdJGNA7PA4MetbLUwjlBFvE?usp=sharing) or train the model yourself using ```trainmodel.py```
3. Add email and password in config file and change options if needed.
4. Run ```python kbb.py```
## Applications
Applications include automatically placing bets on players available on the market based on model predictions and aiding managers in purchase decisions by forecasting price movements.
## Input data
Currently, the model recieves only past marketvalues and whether the player was fit or not as training data. It is believed however that the players club, position and point value could influence the price development. Including any of these parameters poses a fair challenge, be it because of the way the N-HiTS model is accessed via Darts or the nature of the parameter itself (points change only every 7 days at most and sometimes not at all), which is why including them is not a pressing matter.
