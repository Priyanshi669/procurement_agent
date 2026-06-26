import pandas as pd
from services.postgres_manager.utils import engine
from env import get_df


def load_dataset():

    df = get_df()

    df.to_sql(
        "procurement",
        engine,
        if_exists="append",
        index=False,
    )

    print("Dataset loaded successfully.")