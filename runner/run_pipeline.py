from typing import Dict
import pandas as pd
from blocks.pipeline import Pipeline
from type import Evaluators
from .store import Store
from typing import List, Union
from .integrity import check_integrity
from pprint import pprint
from .evaluation import evaluate
import os
import datetime
from configs import Const


def run_pipeline(
    pipeline: Pipeline,
    data: Dict[str, Union[pd.Series, List]],
    labels: pd.Series,
    evaluators: Evaluators,
    train: bool,
) -> List:

    path = (
        Const.output_path
        + "/runs/"
        + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        + "/"
    )
    os.mkdir(path)

    print("🗼 Hierarchy of Models:")
    pprint(pipeline.children())

    print("🆔 Verifying pipeline integrity")
    if not check_integrity(pipeline):
        raise Exception("Pipeline integrity check failed")

    store = Store(data, labels)

    print("💈 Loading existing models")
    pipeline.load()

    print("📡 Looking for remote models")
    pipeline.load_remote()

    if train:
        print("🏋️ Training pipeline")
        pipeline.fit(store)

        print("📡 Uploading models")
        pipeline.save_remote()

    print("🔮 Predicting with pipeline")
    preds_probs = pipeline.predict(store)
    predictions = [pred[0] for pred in preds_probs]

    evaluate(predictions, store, evaluators, path)

    return predictions
