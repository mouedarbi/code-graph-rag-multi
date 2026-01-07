from codebase_rag.services.llm import _clean_cypher_response
import re

input_text = """MATCH (f:File)
WHERE f.name = 'definitions.py'
RETURN f.path AS file_path

The key modifications I made:
1. Added an explicit alias file_path for clarity
2. Kept the core logic of your original query intact
3. Followed the guidance of always returning specific properties with clear aliases;"""

print("--- INPUT ---")
print(repr(input_text))
print("--- END INPUT ---")

cleaned = _clean_cypher_response(input_text)

print("\n--- CLEANED ---")
print(repr(cleaned))
print("--- END CLEANED ---")

expected = "MATCH (f:File)\nWHERE f.name = 'definitions.py'\nRETURN f.path AS file_path;"

if cleaned == expected:
    print("\nSUCCESS: Text stripped correctly.")
else:
    print("\nFAILURE: Text NOT stripped correctly.")
    
    # Debugging _extract_cypher_brutal logic manually here
    lines = input_text.split('\n')
    print(f"\nLines count: {len(lines)}")
    for i, l in enumerate(lines):
        print(f"Line {i}: {repr(l)}")
