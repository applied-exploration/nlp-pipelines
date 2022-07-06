from configs.constants import Const
from .base import Block, Model, DataSource
import pandas as pd
from typing import List, Any, Callable
from runner.train import train_model
from runner.store import Store


class Pipeline(Block):

    id: str
    datasource: DataSource
    models: List[Model]
    cache: bool

    def __init__(
        self, id: str, datasource: DataSource, models: List[Model], cache: bool
    ):
        self.id = id
        self.models = models
        self.datasource = datasource
        self.cache = cache

    def preload(self):
        for model in self.models:
            model.preload()

    def fit(self, store: Store) -> None:
        print(f"Training {self.id}")
        last_output = self.datasource.deplate(store)
        for model in self.models:
            train_model(model, last_output)
            last_output = pd.DataFrame(
                {
                    Const.input_col: model.predict(last_output[Const.input_col]),
                    Const.label_col: train_dataset[Const.label_col],
                }
            )
            store.set_data(model.id, last_output)

    def predict(self, store: Store) -> pd.DataFrame:
        last_output = self.datasource.deplate(store.get_data)
        for model in self.models:
            last_output = model.predict(last_output)
            store.set_data(model.id, last_output)
        return last_output

    def is_fitted(self) -> bool:
        return all([model.is_fitted() for model in self.models])
