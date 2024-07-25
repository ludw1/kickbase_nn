from darts.models import NHiTSModel
from darts import TimeSeries
from darts.metrics import mape, mse, rmse, mae, r2_score
from typing import Optional, Union
import pandas as pd
import matplotlib.pyplot as plt
from train_model.dataloader import dataloader
from darts.dataprocessing.transformers import Scaler
def display_forecast(
    pred_series: TimeSeries,
    observed_series: TimeSeries,
    forecast_type: str,
    start_date: Optional[Union[pd.Timestamp, float, int]] = None,
) -> None:
    """
    Plot observed versus predicted data.

    :param pred_series (TimeSeries): The predicted series
    :param observed_series (TimeSeries): The observed series
    :param forecast_type (str): Horizon, e.g. 7 days
    :param start_date (Optional[Union[Timestamp, float, int]]): Start of 'observed_series'
    :return: None
    """
    plt.figure(figsize=(8, 5))
    if start_date:
        observed_series = observed_series.drop_before(start_date)
    observed_series.univariate_component(0).plot(label="actual")
    pred_series.plot(label=("historic " + forecast_type + " forecasts"))
    plt.title(
        "MAPE: {}".format(mape(observed_series.univariate_component(0), pred_series))
    )
    plt.legend()

    MSE = mse(observed_series.univariate_component(0), pred_series)
    RMSE = rmse(observed_series.univariate_component(0), pred_series)
    MAE = mae(observed_series.univariate_component(0), pred_series)
    MAPE = mape(observed_series.univariate_component(0), pred_series)
    R2 = r2_score(observed_series.univariate_component(0), pred_series)
    # std = np.std(observed_series.univariate_component(0))

    print(f" MSE: {MSE}\n RMSE: {RMSE}\n MAE: {MAE}\n MAPE: {MAPE}\n R2: {R2}")

file_path = r"testdata.csv" # path to csv file with marketvalues
input_len, output_len = 33, 2 # optimal parameters determined by hyperparameter tuning
player_data, fit_data = dataloader(file_path, True, input_len, output_len, False)
scaler = Scaler()
player_name = "Thomas Müller"
# select one player for prediction
selected_player = scaler.fit_transform(player_data[player_name])

selected_player_cov = fit_data[player_name].append_values([1]*100)
model = NHiTSModel.load(r"NHiTSModel_2024-07-19_11_24_34.pt")
# hist_pred = model.historical_forecasts(selected_player, forecast_horizon=2, past_covariates=selected_player_cov, retrain = False, verbose=True)
# display_forecast(hist_pred, selected_player, "2 days")
plt.show()
pred = model.predict(n = 6, series = selected_player, past_covariates=selected_player_cov)
scaler.inverse_transform(pred).plot(label="forecast")
print(scaler.inverse_transform(pred))
scaler.inverse_transform(selected_player).plot(label="actual")
plt.show()
combined = selected_player.append(pred)
scaler.inverse_transform(combined).plot(label="combined")
plt.show()