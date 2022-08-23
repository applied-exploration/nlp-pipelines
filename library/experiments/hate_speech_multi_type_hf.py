from copy import deepcopy
from enum import Enum


from blocks.concat import DataSource, VectorConcat

from blocks.models.huggingface import HuggingfaceModel
from blocks.pipeline import Pipeline

from library.evaluation.classification import classification_metrics
from transformers.training_args import TrainingArguments
from type import (
    DatasetSplit,
    HuggingfaceConfig,
    Experiment,
    HFTaskTypes,
)
from blocks.models.sklearn import SKLearnModel
from blocks.adaptors.classification_output import ClassificationOutputAdaptor

from ..dataset.tweet_eval import get_tweet_eval_dataloader
from ..models.sklearn_voting import sklearn_config
from ..dataset.dynahate import get_dynahate_dataloader

""" Models """

huggingface_training_args = TrainingArguments(
    output_dir="",
    learning_rate=2e-5,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=16,
    num_train_epochs=0.01,
    weight_decay=0.01,
    save_strategy="epoch",
    log_level="critical",
    report_to="none",
    optim="adamw_torch",
    logging_strategy="steps",
    evaluation_strategy="epoch",
    logging_steps=1,
    # eval_steps = 10
)


class HFModels(Enum):
    distilbert_base_uncased = "distilbert-base-uncased"
    distilroberta_base = "distilroberta-base"
    distilbert_emotion = "bhadresh-savani/distilbert-base-uncased-emotion"


huggingface_base_config = HuggingfaceConfig(
    preferred_load_origin=None,  # LoadOrigin.local,
    pretrained_model=HFModels.distilbert_base_uncased.value,
    user_name="semy",
    task_type=HFTaskTypes.sentiment_analysis,
    remote_name_override=None,
    save_remote=True,
    save=True,
    num_classes=2,
    val_size=0.1,
    frozen=False,
    training_args=huggingface_training_args,
)


huggingface_distil_bert_config = huggingface_base_config


huggingface_distilbert_uncased_emotion_config = (
    huggingface_base_config.set_attr(
        "pretrained_model", HFModels.distilbert_emotion.value
    )
    .set_attr("num_classes", 6)
    .set_attr("task_type", HFTaskTypes.text_classification)
    .set_attr("frozen", True)
)


""" Data """

tweet_eval_hate = DataSource("tweet_eval_hate", get_tweet_eval_dataloader("hate"))
dynahate = DataSource("dynahate", get_dynahate_dataloader())


""" Pipelines"""

hf_distilbert = Pipeline(
    "hf-pipeline",
    datasource=tweet_eval_hate,
    models=[
        HuggingfaceModel(
            "distilbert-binary",
            huggingface_distil_bert_config,
            dict_lookup={"LABEL_0": 0, "LABEL_1": 1},
        ),
        ClassificationOutputAdaptor(select=0),
    ],
)

hf_distilbert_uncased_emotion = Pipeline(
    "hf-pipeline",
    datasource=dynahate,
    models=[
        HuggingfaceModel(
            "distilbert-multiclass",
            huggingface_distilbert_uncased_emotion_config,
            dict_lookup={
                "sadness": 0,
                "joy": 1,
                "anger": 2,
                "fear": 3,
                "love": 4,
                "surprise": 5,
            },
        ),
        ClassificationOutputAdaptor(select=0),
    ],
    datasource_predict=tweet_eval_hate,
)

vector_concat = VectorConcat(
    "concat-source",
    [hf_distilbert, hf_distilbert_uncased_emotion],
    datasource_labels=tweet_eval_hate,
)

full_pipeline = Pipeline(
    "hf-multi-objective-pipeline",
    datasource=vector_concat,
    models=[
        SKLearnModel("sklearn-meta-model", sklearn_config),
    ],
)

metrics = classification_metrics

""" Experiments """
multi_type_hf_run_experiments = [
    Experiment(
        project_name="hate-speech-detection-hf",
        run_name="hf-multi-objective",
        dataset_category=DatasetSplit.train,
        pipeline=full_pipeline,
        metrics=metrics,
        train=True,
    ),
    Experiment(
        project_name="hate-speech-detection-hf",
        run_name="hf-multi-objective",
        dataset_category=DatasetSplit.test,
        pipeline=full_pipeline,
        metrics=metrics,
        train=False,
    ),
]
