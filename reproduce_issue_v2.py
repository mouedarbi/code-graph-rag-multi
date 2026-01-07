from codebase_rag.services.llm import _clean_cypher_response

problematic_input = """Here's the Cypher query you requested:

cypher
MATCH (c:Class {name: 'ObservationEngine'})
RETURN c.path


This query will:
1. Find the Class node with the exact name 'ObservationEngine'
2. Return the path property of that class

Note: If you want a more robust search that handles potential case variations or partial matches, you might consider:

cypher
MATCH (c:Class)
WHERE toLower(c.name) = toLower('ObservationEngine')
RETURN c.path
;"""

print(f"Input:\n---\n{problematic_input}\n---\n")
cleaned = _clean_cypher_response(problematic_input)
print(f"Cleaned:\n---\n{cleaned}\n---\n")

expected_start = "MATCH (c:Class {name: 'ObservationEngine'})"
expected_end = "RETURN c.path;"

# Normalize newlines for comparison
cleaned_normalized = cleaned.replace('\n', ' ').replace('  ', ' ').strip()

if cleaned.startswith(expected_start) and cleaned.endswith(";"):
    if "Here's the Cypher query" not in cleaned and "Note:" not in cleaned:
         print("SUCCESS: Query cleaned correctly.")
    else:
         print("FAILURE: Query contains conversational text.")
else:
    print("FAILURE: Query was not cleaned correctly.")
    print(f"Expected start with '{expected_start}' and end with ';'.")
