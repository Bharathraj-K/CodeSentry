from app.llm_analyzer_lmstudio import CodeAnalyzer

# Initialize LM Studio analyzer
print("Initializing LM Studio Code Analyzer...")
print("Make sure LM Studio is running with a model loaded!")
print("=" * 60)
print()

analyzer = CodeAnalyzer(base_url="http://localhost:1234/v1", model="local-model")
print()

# Test 1: Code with potential bug
print("=" * 60)
print("TEST 1: Code with potential bug")
print("=" * 60)

test_code_1 = """
+ def calculate_total(items):
+     total = 0
+     for item in items:
+         total += item.price
+     return total
"""

print("Analyzing code...")
review_1 = analyzer.analyze_code(test_code_1, "cart.py")
print(review_1)
print("\n")

# Test 2: Code with security issue
print("=" * 60)
print("TEST 2: Code with SQL injection risk")
print("=" * 60)

test_code_2 = """
+ def get_user(username):
+     query = f"SELECT * FROM users WHERE name = '{username}'"
+     return db.execute(query)
"""

print("Analyzing code...")
review_2 = analyzer.analyze_code(test_code_2, "database.py")
print(review_2)
print("\n")

# Test 3: Code with bad practice
print("=" * 60)
print("TEST 3: Code with bad practices")
print("=" * 60)

test_code_3 = """
+ def process_data(data):
+     result = []
+     for i in range(len(data)):
+         result.append(data[i] * 2)
+     return result
"""

print("Analyzing code...")
review_3 = analyzer.analyze_code(test_code_3, "utils.py")
print(review_3)
print("\n")

# Test 4: Good code
print("=" * 60)
print("TEST 4: Well-written code")
print("=" * 60)

test_code_4 = """
+ def calculate_average(numbers: list[float]) -> float:
+     '''Calculate the average of a list of numbers.'''
+     if not numbers:
+         raise ValueError("Cannot calculate average of empty list")
+     return sum(numbers) / len(numbers)
"""

print("Analyzing code...")
review_4 = analyzer.analyze_code(test_code_4, "math_utils.py")
print(review_4)
print("\n")

print("=" * 60)
print("ALL TESTS COMPLETED")
print("=" * 60)