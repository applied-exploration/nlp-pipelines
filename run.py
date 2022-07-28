from configs.constants import Const
from data.dataloader import transform_dataset
from datasets import load_dataset
from runner.runner import Runner
from library.examples.hate_speech import (
    ensemble_pipeline,
    preprocess_config,
)
from library.evaluation import classification_metrics

from blocks.pipeline import Pipeline
from typing import List
from plugins import WandbPlugin, WandbConfig
from type import PreprocessConfig, TestDataset, TrainDataset, RunConfig






def run(
    pipeline: Pipeline,
    preprocess_config: PreprocessConfig,
    project_id: str,
    run_configs: List[RunConfig],
) -> None:

    for config in run_configs:
        logger_plugins = [
            WandbPlugin(
                WandbConfig(
                    project_id=project_id,
                    run_name=config.run_name + "-" + pipeline.id,
                    train=True,
                ),
                dict(
                    run_config=config.get_configs(),
                    preprocess_config=preprocess_config.get_configs(),
                    pipeline_configs=pipeline.get_configs(),
                ),
            )
        ]
        runner = Runner(
            config,
            pipeline,
            data={Const.input_col: config.dataset[Const.input_col]},
            labels=config.dataset[Const.label_col]
            if hasattr(config.dataset, Const.label_col)
            else None,
            evaluators=classification_metrics,
            plugins=logger_plugins if config.remote_logging else [],
        )
        runner.run()


if __name__ == "__main__":
    hate_speech_data = transform_dataset(
    load_dataset("tweet_eval", "hate"), preprocess_config
    )
    run_configs = [
        RunConfig(
            run_name="hate-speech-detection", dataset=hate_speech_data[0], train=True
        ),
        RunConfig(
            run_name="hate-speech-detection", dataset=hate_speech_data[1], train=False
        ),
    ]

    run(
        sklearn_ensemble,
        preprocess_config,
        project_id="hate-speech-detection",
        run_configs=run_configs,
    )
