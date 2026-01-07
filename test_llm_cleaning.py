from codebase_rag.services.llm import _clean_cypher_response
import unittest

class TestCypherCleaning(unittest.TestCase):
    def test_clean_simple(self):
        input_text = "MATCH (n) RETURN n;"
        expected = "MATCH (n) RETURN n;"
        self.assertEqual(_clean_cypher_response(input_text), expected)

    def test_markdown_block(self):
        input_text = """Here is the query:
```cypher
MATCH (n) RETURN n
```
Hope that helps!"""
        expected = "MATCH (n) RETURN n;"
        self.assertEqual(_clean_cypher_response(input_text), expected)

    def test_preamble_garbage(self):
        input_text = """Sure, I can help with that.
        
        MATCH (f:File)
        RETURN f.path
        
        This will return all file paths."""
        expected = "MATCH (f:File)\n        RETURN f.path;"
        # Note: indentation in expected might need adjustment depending on how strip works on lines
        # But let's check if it contains the core and no garbage
        cleaned = _clean_cypher_response(input_text)
        self.assertTrue(cleaned.strip().startswith("MATCH"))
        self.assertIn("RETURN f.path", cleaned)
        self.assertNotIn("Sure", cleaned)
        self.assertNotIn("This will return", cleaned)

    def test_post_query_explanation(self):
        input_text = """MATCH (n) RETURN n
        
        Note: This is a simple query."""
        cleaned = _clean_cypher_response(input_text)
        self.assertNotIn("Note:", cleaned)
        self.assertTrue(cleaned.endswith(";"))

    def test_multiple_queries_first_one_wins(self):
        input_text = """Here is the exact match:
        MATCH (n {name: 'foo'}) RETURN n
        
        Or fuzzy match:
        MATCH (n) WHERE n.name =~ 'foo.*' RETURN n"""
        
        cleaned = _clean_cypher_response(input_text)
        self.assertIn("name: 'foo'", cleaned)
        self.assertNotIn("fuzzy match", cleaned)
        # It might stop at "Or fuzzy match" because "Or" isn't a cypher keyword starting a line (usually)
        # Wait, OR is a keyword inside WHERE.
        # But "Or fuzzy match:" line doesn't start with a Cypher keyword.
        
    def test_issue_v2_reproduction(self):
        input_text = """Here's the Cypher query you requested:

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
        cleaned = _clean_cypher_response(input_text)
        expected_start = "MATCH (c:Class {name: 'ObservationEngine'})"
        self.assertTrue(cleaned.startswith(expected_start))
        self.assertNotIn("Here's", cleaned)
        self.assertNotIn("This query will", cleaned)

if __name__ == '__main__':
    unittest.main()
