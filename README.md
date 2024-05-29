# Overview
Project to use a neural net, more specifically the Transformers architecture, to predict marketvalues of players on the popular football fantasy manager [kickbase.com](https://www.kickbase.com). Using a [N-HiTS model](https://unit8co.github.io/darts/generated_api/darts.models.forecasting.nhits.html) and the [Darts python package](https://unit8co.github.io/darts/index.html) the player data is converted into a time series and subsequently fed into the neural net. 
## Usage
Because N-HiTS requires PyTorch, only using python version <=3.11.x is possible. After installing the necessary packages using ```pip install -r requirements.txt```, you need to set the filepath variable in the file _trainmodel.py_ to the path where the csv with the market values lies. Then simply running the file _trainmodel.py_ will train the model and save it.
## Applications
Applications include automatically placing bets on players available on the market based on model predictions and aiding managers in purchase decisions by forecasting price movements.
## Input data
Currently, the model recieves only past marketvalues and whether the player was fit or not as training data. It is believed however that the players club, position and point value could influence the price development. Including any of these parameters poses a fair challenge, be it because of the way the N-HiTS model is accessed via Darts or the nature of the parameter itself (points change only every 7 days at most and sometimes not at all), which is why including them is not a pressing matter.
