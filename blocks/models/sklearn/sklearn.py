import pandas as pd
from sklearn.multiclass import OneVsRestClassifier
from sklearn.base import ClassifierMixin
from imblearn.over_sampling import RandomOverSampler
from imblearn.pipeline import Pipeline as ImbPipeline
from blocks.models.base import Model
from type import SKLearnConfig, DataType
from configs.constants import Const
from typing import Optional


class SKLearnModel(Model):

    config: SKLearnConfig

    inputTypes = [DataType.Series, DataType.List, DataType.NpArray]
    outputType = DataType.PredictionsWithProbs

    def __init__(self, id: str, config: SKLearnConfig):
        self.id = id
        self.config = config
        self.model = None
        self.trained = False

    def fit(self, dataset: pd.Series, labels: Optional[pd.Series]) -> None:

        self.model = ImbPipeline(
            [
                # ('feature_selection', SelectPercentile(chi2, percentile=50)),
                ("sampling", RandomOverSampler()),
                ("clf", self.config.classifier),
            ],
            verbose=True,
        )

        self.model.fit(dataset, labels)
        self.trained = True

    def predict(self, dataset: pd.Series) -> pd.Series:
        predictions = self.model.predict(dataset)
        probabilities = [tuple(row) for row in self.model.predict_proba(dataset)]

        return pd.DataFrame(
            {Const.preds_col: predictions, Const.probs_col: probabilities}
        )

    def is_fitted(self) -> bool:
        return self.model is not None


def create_classifier(
    classifier: ClassifierMixin, one_vs_rest: bool
) -> ClassifierMixin:
    if one_vs_rest:
        return classifier
    else:
        return OneVsRestClassifier(
            ("clf", classifier),
            n_jobs=4,
        )
