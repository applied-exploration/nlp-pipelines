from data.dataloader import load_data
from run import run

from library.examples.hate_speech import (
    huggingface_baseline,
    nlp_sklearn,
    nlp_sklearn_autocorrect,
    text_statistics_pipeline,
    ensemble_pipeline,
    # preprocess_config,
)
from type import PreprocessConfig

preprocess_config = PreprocessConfig(
    train_size=-1,
    val_size=-1,
    test_size=-1,
    input_col="text",
    label_col="label",
)

hate_speech_data = load_data("data/original", preprocess_config)

train_data, test_data = hate_speech_data

for pipeline in [
    huggingface_baseline,
    nlp_sklearn,
    nlp_sklearn_autocorrect,
    text_statistics_pipeline,
    ensemble_pipeline,
]:
    run(
        pipeline,
        hate_speech_data,
        preprocess_config,
        project_id="hate-speech-detection",
    )
