from darts.models import NHiTSModel
from pytorch_lightning.callbacks import EarlyStopping
from darts.dataprocessing.transformers import Scaler
from train_model.dataloader import dataloader
def define_nhits_model(in_len, out_len):
    """
    Setup the NHiTS model
    :param in_len: int: Input length
    :param out_len: int: Output length
    :return: NHiTSModel: NHiTS model
    """
    early_stopper = EarlyStopping(
    monitor="val_loss",
    patience=5,
    min_delta=0.05,
    mode='min',
    )

    callbacks = [early_stopper]
    pl_trainer_kwargs = {
        "accelerator": "auto",
        "callbacks": callbacks
    }
    model = NHiTSModel(
        input_chunk_length = in_len,
        output_chunk_length = out_len,
        n_epochs = 20,
        batch_size = 300,
        num_blocks = 8,
        num_layers = 3,
        layer_widths = 512,
        random_state = 0,
        model_name = "NHits",
        add_encoders={
        'cyclic': {'past': ['month']},
        'datetime_attribute': {'past': ['dayofweek']},
        'position': {'past': ['relative']},
        'transformer': Scaler(),
        'tz': 'CET'
        },
        pl_trainer_kwargs = pl_trainer_kwargs
    )
    return model

file_path = r"" # path to csv file with marketvalues
input_len, output_len = 33, 2 # optimal parameters determined by hyperparameter tuning
data = dataloader(file_path, True, input_len, output_len)
train, val, pastcov_t, pastcov_val, raw = data
model = define_nhits_model(input_len, output_len)
model.fit(series = train, val_series = val, past_covariates = pastcov_t, val_past_covariates = pastcov_val, verbose=True)
model.save()