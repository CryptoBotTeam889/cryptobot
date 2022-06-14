import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OrdinalEncoder, RobustScaler


def create_pipeline(df):
    num_cat_list = (
        df.drop(columns=["target"])
        .select_dtypes(include=["float64", "int64"])
        .columns.values.tolist()
    )
    cat_col_list = ["FG_val_clasif"]

    num_scaler = RobustScaler()
    cat_encoder = OrdinalEncoder(
        categories=[["Extreme Fear", "Fear", "Neutral", "Greed", "Extreme Greed"]],
        dtype=np.int64,
        handle_unknown="use_encoded_value",
        unknown_value=-999,
    )

    col_transformer = ColumnTransformer(
        [
            ("num_tr", num_scaler, num_cat_list),
            ("cat_tr", cat_encoder, cat_col_list),
        ],
        remainder="passthrough",
    )

    return Pipeline(steps=[("Col_transformer", col_transformer)])
