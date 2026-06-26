import psycopg2
from psycopg2.extras import RealDictCursor

from services.postgres_manager.utils import DB_URL, llm, model

SCHEMA = """
Table: procurement

Columns:
- TransactionID (TEXT, Primary Key)
- ItemName (TEXT)
- Category (TEXT)           
- Quantity (INTEGER)
- UnitPrice (FLOAT)
- TotalCost (FLOAT)
- PurchaseDate (DATE)
- Supplier (TEXT)
- Buyer (TEXT)
"""

# SQL_SYSTEM = f"""You are a PostgreSQL expert. Convert the user's question into a valid SQL query.
# Return ONLY the raw SQL — no explanation, no markdown, no backticks.

# Schema:
# {SCHEMA}

# Rules:
# - Return raw SQL only, nothing else
# - Add LIMIT 100 unless the question asks for aggregates or all rows
# - Use TRUE/FALSE for booleans
# - Return ONE single SQL query only — never multiple statements
# """


# def get_sql(question: str) -> str:
#     messages = [
#         {"role": "system", "content": SQL_SYSTEM},
#         {"role": "user", "content": question},
#     ]
#     response = llm.chat.completions.create(
#         model=model,
#         messages=messages,
#         temperature=0.3,
#         max_tokens=800,
#     )
#     print("sql generated")
#     return response.choices[0].message.content.strip()


def run_sql(sql: str) -> list[dict]:
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(sql)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    print("sql run on db")
    return rows