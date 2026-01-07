from codebase_rag.services.llm import _clean_cypher_response

input_text = "MATCH (f:File)\nWHERE f.name = 'definitions.py'\nRETURN f.path AS file_path\n\nThe query remains essentially the same, but I've added an alias file_path to follow the best practice of always returning properties with clear aliases. This makes the result more semantically clear and follows the guidelines for Cypher query formatting.";

print(f"Input length: {len(input_text)}")
print("--- INPUT ---")
print(input_text)
print("--- END INPUT ---")

cleaned = _clean_cypher_response(input_text)

print("\n--- CLEANED ---")
print(cleaned)
print("--- END CLEANED ---")

expected = "MATCH (f:File)\nWHERE f.name = 'definitions.py'\nRETURN f.path AS file_path;"
cleaned_norm = cleaned.replace('\n', ' ').strip()
expected_norm = expected.replace('\n', ' ').strip()

if cleaned.strip() == expected.strip() or cleaned_norm == expected_norm:
    print("\nSUCCESS: Text stripped correctly.")
else:
    print("\nFAILURE: Text NOT stripped correctly.")
