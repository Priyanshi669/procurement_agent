from agents import function_tool

from services.weaviate_manager.retreival import _search_order_impl, SearchOrderOutput, OrderDetails
from services.postgres_manager.retreival import run_sql


@function_tool
def create_order():
    print("order placed")


@function_tool
def postgres_search(question: str) -> SearchOrderOutput:
    """
    Answer procurement questions using PostgreSQL.
    Looks up a transaction by id from the procurement database.
    """
    print("postgres")
    
    try:
        
        sql = f"""SELECT * FROM procurement WHERE "TransactionID" ='{question}'"""
        print(sql)
        rows = run_sql(sql)   # see note below on run_sql_params

        orders = [
            OrderDetails(
                transaction_id=str(_get_col(row, "transactionid", "TransactionID")),
                item_name=_get_col(row, "itemname", "ItemName"),
                supplier=_get_col(row, "supplier", "Supplier"),
                buyer=_get_col(row, "buyer", "Buyer"),
                quantity=_get_col(row, "quantity", "Quantity"),
                total_cost=_get_col(row, "totalcost", "TotalCost"),
                purchase_date=str(_get_col(row, "purchasedate", "PurchaseDate")),
            )
            for row in rows
        ]

        print(f"postgres_search found {len(orders)} orders")
        return SearchOrderOutput(found=len(orders) > 0, total_results=len(orders), orders=orders)

    except Exception as e:
        print(f"TOOL FAILED: {e!r}")
        return SearchOrderOutput(found=False, total_results=0, orders=[], error=True)


def _get_col(row: dict, *candidates: str):
    """Try several possible casings/names for a column."""
    for key in candidates:
        if key in row:
            return row[key]
    raise KeyError(f"None of {candidates} found in row keys {list(row.keys())}")

@function_tool
def semantic_search(product_name: str) -> SearchOrderOutput:
    print(f"[TOOL CALLED] semantic_search({product_name})")

    try:
        result = _search_order_impl(product_name)

        print(result)
        print(f"[TOOL RESULT] found={result.found}")
        return result

    except Exception as e:
        print("TOOL FAILED")
        print(repr(e))
        raise