from .base import Adaptor
import pandas as pd
import numpy as np
from configs.constants import Const
from type import DataType


class DfToNumpy(Adaptor):

    inputTypes = DataType.Series
    outputType = DataType.NpArray

    def predict(self, dataset: pd.DataFrame) -> np.ndarray:
        assert len(dataset) > 0, "Dataset is empty"

        if isinstance(dataset[Const.input_col].iloc[0], (list or np.ndarray)):
            return np.vstack(list(dataset[Const.input_col]))
        elif isinstance(dataset[Const.input_col].iloc[0], (int or float)):
            return dataset[Const.input_col].to_numpy()
        else:
            assert False, "Unsupported conversion type"
