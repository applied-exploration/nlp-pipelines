from type import BaseConfig
from abc import ABC
import pandas as pd
from typing import Optional
from runner.store import Store
from blocks.iomanager import safe_loading, safe_saving


class Element(ABC):
    id: str


class Block(Element):
    config: BaseConfig

    def __init__(
        self, id: Optional[str] = None, config: Optional[BaseConfig] = None
    ) -> None:
        self.id = self.__class__.__name__ if id is None else id
        self.config = (
            BaseConfig(force_fit=False, save=True) if config is None else config
        )

    def load(self, pipeline_id: str, execution_order: int) -> None:
        self.pipeline_id = pipeline_id
        self.id += f"-{str(execution_order)}"

        model = safe_loading(pipeline_id, self.id)
        if model is not None:
            self.model = model

    def load_remote(self) -> None:
        pass

    def fit(self, dataset: pd.DataFrame, labels: Optional[pd.Series]) -> None:
        raise NotImplementedError()

    def predict(self, dataset: pd.DataFrame) -> pd.DataFrame:
        raise NotImplementedError()

    def is_fitted(self) -> bool:
        raise NotImplementedError()

    def save(self) -> None:
        if hasattr(self, "trained") and self.trained:
            safe_saving(self.model, self.pipeline_id, self.id)

    def save_remote(self) -> None:
        pass


class DataSource(Element):

    id: str

    def __init__(self, id: str):
        self.id = id

    def deplate(self, store: Store) -> pd.DataFrame:
        return store.get_data(self.id)

    def load_remote(self):
        pass
