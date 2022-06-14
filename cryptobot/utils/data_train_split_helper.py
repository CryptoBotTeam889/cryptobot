import numpy as np

"""
Defining Subsampling fuction
"""


def subsample_sequence(df, length):

    last_possible = df.shape[0] - length - 1

    random_start = np.random.randint(0, last_possible)
    X = df[random_start : random_start + length].values
    y = df.iloc[random_start + length + 1]["remainder__target"]

    return X, y


"""
Defining fuction to create X and y using Subsampling function
"""


def get_X_y(df, length_of_observations):
    X, y = [], []

    for length in length_of_observations:
        xi, yi = subsample_sequence(df, length)
        X.append(xi)
        y.append(yi)

    return X, y


"""
Splitting data into train and test dataframes
"""


def split_train_test_data(df, percentage_of_test_data=0.8, horizon=1):
    gap = horizon - 1

    len_ = int(percentage_of_test_data * df.shape[0])

    df_train = df[:len_]
    df_test = df[len_ + gap :]

    return df_train, df_test
