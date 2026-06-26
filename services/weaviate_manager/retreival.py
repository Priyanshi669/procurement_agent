from typing import List

from agents import function_tool
from pydantic import BaseModel

from services.weaviate_manager.utils import client, get_embedding


COLLECTION_NAME = "Order"
# ADD this function, right after your imports / COLLECTION_NAME line

def _get_prop(props: dict, key: str):
    """Weaviate auto-lowercases the first letter of property names
    when no explicit schema was given at collection-creation time.
    Try the original casing first, then the lowercased-first-letter form."""
    if key in props:
        return props[key]
    alt = key[0].lower() + key[1:]
    if alt in props:
        return props[alt]
    raise KeyError(f"Property '{key}' not found in {list(props.keys())}")

class OrderDetails(BaseModel):
    transaction_id: str
    item_name: str
    supplier: str
    buyer: str
    quantity: int
    total_cost: float
    purchase_date: str


class SearchOrderOutput(BaseModel):
    err: bool=False
    found: bool
    total_results: int
    orders: List[OrderDetails]


def _search_order_impl(query: str) -> SearchOrderOutput:

    print("=" * 60)
    print(f"Searching : {query}")

    collection = client.collections.get(COLLECTION_NAME)

    query_vector = get_embedding(query)

    response = collection.query.hybrid(
        query=query,
        vector={
            "ItemName_vector": query_vector,
            "Supplier_vector": query_vector,
            "Buyer_vector": query_vector,
            "Category_vector":query_vector,
            
        },
        target_vector=[
            "ItemName_vector",
            "Supplier_vector",
            "Buyer_vector",
            "Category_vector"
        ],
        alpha=0.7,
        limit=5,
    )

    orders = []

    for obj in response.objects:
        props = obj.properties
        orders.append(
            OrderDetails(
                transaction_id=str(_get_prop(props, "TransactionID")),
                item_name=_get_prop(props, "ItemName"),
                supplier=_get_prop(props, "Supplier"),
                buyer=_get_prop(props, "Buyer"),
                quantity=int(_get_prop(props, "Quantity")),
                total_cost=float(_get_prop(props, "TotalCost")),
                purchase_date=str(_get_prop(props, "PurchaseDate")),
            )
        )

    print(f"Found {len(orders)} orders")

    return SearchOrderOutput(
        found=len(orders) > 0,
        total_results=len(orders),
        orders=orders,
    )


@function_tool
def semantic_search(product_name: str) -> SearchOrderOutput:
    print(f"[TOOL] semantic_search({product_name})")
    return _search_order_impl(product_name)