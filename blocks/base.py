from type import BaseConfig, DataType
from abc import ABC
import pandas as pd
from typing import Optional, Union, List
from runner.store import Store
from blocks.iomanager import safe_loading, safe_saving


class Element(ABC):
    id: str

    inputTypes: Union[List[DataType], DataType]
    outputType: DataType

    def children(self) -> List["Element"]:
        raise NotImplementedError()


class Block(Element):
    config: BaseConfig

    def __init__(self, id: Optional[str] = None) -> None:
        self.id = self.__class__.__name__ if id is None else id
        if self.inputTypes is None:
            print("inputTypes must be set")
        if self.outputType is None:
            print("outputType must be set")

    def load(self, pipeline_id: str, execution_order: int) -> None:
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

    def save(self, pipeline_id: str) -> None:
        if hasattr(self, "trained") and self.trained:
            safe_saving(self.model, pipeline_id, self.id)

    def save_remote(self, pipeline_id: str) -> None:
        pass


class DataSource(Element):

    id: str

    inputTypes = DataType.Any
    outputType = DataType.Series

    def __init__(self, id: str):
        self.id = id

    def deplate(self, store: Store) -> pd.DataFrame:
        return store.get_data(self.id)

    def load_remote(self):
        pass

    def children(self) -> List["Element"]:
        return [self]
