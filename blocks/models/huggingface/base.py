from blocks.models.base import Model
from .infer import run_inference_pipeline
from .train import run_training_pipeline
from type import HuggingfaceConfig, DataType
from configs.constants import Const
import pandas as pd
from datasets import Dataset, Features, Value, ClassLabel
from typing import List, Tuple, Callable, Optional, Union
from transformers import pipeline, Trainer, PreTrainedModel
from sklearn.model_selection import train_test_split

from configs.constants import Const


def load_pipeline(module: Union[str, PreTrainedModel]) -> Callable:
    return pipeline(task="sentiment-analysis", model=module)


class HuggingfaceModel(Model):

    config: HuggingfaceConfig
    inputTypes = [DataType.Series, DataType.List]
    outputType = DataType.PredictionsWithProbs

    def __init__(self, id: str, config: HuggingfaceConfig):
        self.id = id
        self.config = config
        self.model: Optional[Union[Callable, Trainer]] = None

    def load_remote(self):
        repo_name = self.config.user_name + "/" + self.config.repo_name
        try:
            self.model = load_pipeline(repo_name)
        except:
            print("❌ No model found in huggingface repository")

    def fit(self, dataset: List[str], labels: Optional[pd.Series]) -> None:

        train_dataset, val_dataset = train_test_split(
            pd.DataFrame({Const.input_col: dataset, Const.label_col: labels}),
            test_size=self.config.val_size,
        )

        model = run_training_pipeline(
            from_pandas(train_dataset, self.config.num_classes),
            from_pandas(val_dataset, self.config.num_classes),
            self.config,
        )
        self.model = load_pipeline(model)
        self.trained = True

    def predict(self, dataset: pd.DataFrame) -> pd.DataFrame:
        if self.model:
            model = self.model
        else:
            print(
                f"❌ No fitted model, using inference on pretrained foundational model :{self.config.pretrained_model}"
            )
            model = load_pipeline(self.config.pretrained_model)

        return run_inference_pipeline(
            model,
            from_pandas(dataset, self.config.num_classes),
            self.huggingface_config,
        )

    def is_fitted(self) -> bool:
        return self.model is not None


def from_pandas(df: pd.DataFrame, num_classes: int) -> Dataset:
    return Dataset.from_pandas(
        df,
        features=Features(
            {
                Const.input_col: Value("string"),
                Const.label_col: ClassLabel(num_classes),
            }
        ),
    )
