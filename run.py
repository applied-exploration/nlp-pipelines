from configs.constants import Const

from data.dataloader import load_data
from runner.run_pipeline import run_pipeline
from library.examples.hate_speech import (
    hate_speech_detection_pipeline,
    preprocess_config,
)
from library.examples.all_transformations import all_transformations
from utils.logging import set_global_logging_level

import logging

set_global_logging_level(
    logging.ERROR,
    ["transformers", "nlp", "torch", "tensorflow", "tensorboard", "wandb"],
)

train_dataset, test_dataset = load_data("data/original", preprocess_config)

pipeline = hate_speech_detection_pipeline()
run_pipeline(
    pipeline,
    {"input": train_dataset[Const.input_col]},
    train_dataset[Const.label_col],
    train=True,
)
