import weaviate.classes.config as wc
import pandas as pd
from env import get_df
from services.weaviate_manager.utils import client, model


data = get_df()
data["PurchaseDate"] = pd.to_datetime(data["PurchaseDate"]).dt.strftime("%Y-%m-%dT%H:%M:%SZ")

EMBED_COLUMNS = ["ItemName", "Category", "Supplier", "Buyer"]


def create_embeddings():
    if not client.collections.exists("Order"):
        client.collections.create(
            name="Order",
            vectorizer_config=[
                wc.Configure.NamedVectors.none(name=f"{col}_vector")
                for col in EMBED_COLUMNS
            ]
        )
    print("order")
    order_collection = client.collections.use("Order")

    with order_collection.batch.dynamic() as batch:
        for _, row in data.iterrows():
            content = {k: (v.item() if hasattr(v, "item") else v) for k, v in row.to_dict().items()}
            
            batch.add_object(
                properties=content,
                vector={
                    f"{col}_vector": model.encode(
                        str(content[col]),
                        normalize_embeddings=True
                    ).tolist()
                    for col in EMBED_COLUMNS
                }
            )
            

    print("\nOrder Embeddings Completed\n")
    client.close()