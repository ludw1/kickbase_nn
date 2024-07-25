from darts.models import NHiTSModel
from darts import TimeSeries
import matplotlib.pyplot as plt
from darts.dataprocessing.transformers import Scaler


def nn_predict(input_series : TimeSeries, past_covariates : TimeSeries, model_path : str, n : int):
    """
    Predict future values using the NHiTS model
    :param input_series: TimeSeries: Input series
    :param past_covariates: TimeSeries: Past covariates
    :param model_path: str: Path to model
    :param n: int: Number of predictions
    :return: TimeSeries: Predicted values
    """
    model = NHiTSModel.load(model_path)
    scaler = Scaler()
    input_series = scaler.fit_transform(input_series)
    past_covariates = past_covariates.append_values([1]*100)
    pred = model.predict(n = n, series = input_series, past_covariates=past_covariates)
    return scaler.inverse_transform(pred)