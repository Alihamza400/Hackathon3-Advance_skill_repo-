# Concepts Agent Service - Explains Python concepts with examples
# LearnFlow AI Tutoring Platform

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal
from enum import Enum
from datetime import datetime, timezone
import os
import uuid
import httpx

from shared.base import (
    create_app, settings, logger, cache_get, cache_set,
    publish_event, get_current_user, get_optional_user,
    dapr_client, publish_event, HealthResponse
)

settings.service_name = "concepts-agent"

app = create_app("concepts-agent", "Concepts Agent - Python Concept Explainer")


# ============================================
# Models
# ============================================

class DifficultyLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class ExplainRequest(BaseModel):
    concept: str = Field(..., min_length=1, max_length=200, description="Concept to explain")
    level: DifficultyLevel = Field(default=DifficultyLevel.BEGINNER, description="Target difficulty level")
    context: Optional[str] = Field(None, description="Additional context or specific question")
    student_id: Optional[str] = None
    include_examples: bool = True
    include_visual: bool = False
    include_exercises: bool = True


class CodeExample(BaseModel):
    title: str
    code: str
    explanation: str
    language: str = "python"


class ConceptExplanation(BaseModel):
    concept: str
    level: DifficultyLevel
    definition: str
    explanation: str
    key_points: List[str]
    analogies: List[str] = []
    code_examples: List[CodeExample] = []
    common_mistakes: List[str] = []
    related_concepts: List[str] = []
    practice_exercises: List[Dict[str, Any]] = []
    visual_aid: Optional[Dict[str, Any]] = None
    prerequisites: List[str] = []
    next_steps: List[str] = []
    estimated_reading_time_minutes: int
    metadata: Dict[str, Any] = {}


class ExplainResponse(BaseModel):
    explanation: ConceptExplanation
    follow_up_suggestions: List[str] = []
    related_topics: List[str] = []


# ============================================
# Concept Knowledge Base
# ============================================

CONCEPT_KNOWLEDGE = {
    "variable": {"beginner": {
        "definition": "A variable is a named storage location in memory that holds a value.",
        "explanation": "Think of a variable like a labeled box. You put something in it (assign a value), look at what's inside (read the value), or replace what's inside (reassign). Python automatically manages the type for you.",
        "key_points": ["Variables store data values", "Names are case-sensitive", "Must start with letter or underscore", "Python auto-detects type"],
        "analogies": ["Like a labeled box in a warehouse", "Like a sticky note with a value", "Like a container with a label"],
        "code_examples": [
            {"title": "Basic Assignment", "code": "name = \"Alice\"\nage = 25\nheight = 5.6\nis_student = True\nprint(name, age, height, is_student)", "explanation": "Variables hold different types: string, int, float, bool"},
            {"title": "Reassignment", "code": "x = 10\nprint(x)  # 10\nx = 20\nprint(x)  # 20\nx = \"hello\"\nprint(x)  # hello", "explanation": "Variables can change type when reassigned"},
            {"title": "Multiple Assignment", "code": "a, b, c = 1, 2, 3\nprint(a, b, c)  # 1 2 3\nx = y = z = 0\nprint(x, y, z)  # 0 0 0", "explanation": "Assign multiple variables in one line"}
        ],
        "common_mistakes": ["Using reserved keywords (class, def, for)", "Starting names with numbers", "Confusing = with =="],
        "prerequisites": [], "next_steps": ["data_types", "operators", "strings"],
        "related_concepts": ["data_types", "assignment", "constants"]
    }},
    "function": {"beginner": {
        "definition": "A reusable block of code that performs a specific task.",
        "explanation": "Functions are like recipes — write instructions once, use them over and over with different ingredients (parameters) to get results (return values).",
        "key_points": ["Encapsulate reusable logic", "Take parameters, return values", "DRY principle", "Create local scope"],
        "analogies": ["Like a recipe in a cookbook", "Like a vending machine (input → process → output)", "Like a power tool"],
        "code_examples": [
            {"title": "Basic Function", "code": "def greet(name):\n    return f\"Hello, {name}!\"\n\nprint(greet(\"Alice\"))  # Hello, Alice!", "explanation": "Function takes name parameter, returns greeting"},
            {"title": "Default Parameters", "code": "def greet(name, greeting=\"Hello\"):\n    return f\"{greeting}, {name}!\"\n\nprint(greet(\"Alice\"))        # Hello, Alice!\nprint(greet(\"Bob\", \"Hi\"))    # Hi, Bob!", "explanation": "Default parameters are optional when calling"},
            {"title": "Multiple Returns", "code": "def stats(nums):\n    return min(nums), max(nums), sum(nums)/len(nums)\n\nlo, hi, avg = stats([10, 20, 30])\nprint(f\"Low:{lo} High:{hi} Avg:{avg:.0f}\")", "explanation": "Functions can return multiple values as tuples"}
        ],
        "common_mistakes": ["Forgetting return (returns None)", "Modifying mutable default args", "Not calling with ()"],
        "prerequisites": ["variables"], "next_steps": ["lambda", "decorators", "generators"],
        "related_concepts": ["parameters", "return_values", "scope", "lambda"]
    }},
    "loop": {"beginner": {
        "definition": "A loop repeats a block of code multiple times.",
        "explanation": "Loops automate repetitive tasks — write code once, tell Python how many times or until what condition.",
        "key_points": ["for loops iterate over sequences", "while loops run while condition is True", "break exits early", "continue skips to next iteration"],
        "analogies": ["Like a playlist on repeat", "Like an assembly line", "Like reading every page in a book"],
        "code_examples": [
            {"title": "For Loop with Range", "code": "for i in range(5):\n    print(f\"Count: {i}\")\n# 0 1 2 3 4", "explanation": "range(5) generates 0,1,2,3,4"},
            {"title": "For Loop Over List", "code": "fruits = [\"apple\", \"banana\", \"cherry\"]\nfor fruit in fruits:\n    print(f\"I like {fruit}\")", "explanation": "Iterate directly over collection items"},
            {"title": "While Loop", "code": "count = 0\nwhile count < 3:\n    print(f\"Count: {count}\")\n    count += 1", "explanation": "Runs while condition is True — don't forget to increment!"}
        ],
        "common_mistakes": ["Infinite loops (forgetting increment)", "Off-by-one errors", "Modifying list while iterating"],
        "prerequisites": ["variables", "conditionals"], "next_steps": ["list_comprehensions", "nested_loops"],
        "related_concepts": ["conditionals", "lists", "comprehensions"]
    }},
    "conditional": {"beginner": {
        "definition": "Conditionals let your code make decisions based on boolean conditions.",
        "explanation": "Like a fork in the road — if the condition is true, go one way; otherwise, go another. Python uses if, elif, else.",
        "key_points": ["if checks a condition", "elif adds more checks", "else catches everything else", "Conditions are True/False"],
        "analogies": ["Like a traffic light", "Like a decision flowchart", "Like a GPS choosing routes"],
        "code_examples": [
            {"title": "If/Else", "code": "age = 18\nif age >= 18:\n    print(\"You can vote!\")\nelse:\n    print(\"Too young\")", "explanation": "Simple binary decision"},
            {"title": "Elif Chain", "code": "score = 85\nif score >= 90:\n    grade = \"A\"\nelif score >= 80:\n    grade = \"B\"\nelif score >= 70:\n    grade = \"C\"\nelse:\n    grade = \"F\"\nprint(f\"Grade: {grade}\")", "explanation": "Multiple conditions checked in order"}
        ],
        "common_mistakes": ["Using = instead of ==", "Forgetting colons", "Indentation errors"],
        "prerequisites": ["variables", "operators"], "next_steps": ["ternary", "match_case"],
        "related_concepts": ["operators", "boolean_logic", "loops"]
    }},
    "list": {"beginner": {
        "definition": "A list is an ordered, mutable collection of items in square brackets.",
        "explanation": "Lists store multiple items in a single variable. They can hold any type, are ordered (indexed), and mutable (changeable). Zero-indexed: first item is at index 0.",
        "key_points": ["Ordered collections", "Mutable (add/remove/change)", "Zero-indexed", "Can mix types"],
        "analogies": ["Like a shopping list", "Like a train with carriages", "Like numbered lockers"],
        "code_examples": [
            {"title": "Creating Lists", "code": "fruits = [\"apple\", \"banana\", \"cherry\"]\nnumbers = [1, 2, 3, 4, 5]\nmixed = [1, \"hello\", 3.14, True]\nprint(fruits, numbers, mixed)", "explanation": "Lists can hold any type of data"},
            {"title": "List Indexing", "code": "fruits = [\"apple\", \"banana\", \"cherry\"]\nprint(fruits[0])   # apple\nprint(fruits[-1])  # cherry (negative = from end)\nprint(fruits[1:3]) # ['banana', 'cherry'] (slicing)", "explanation": "Access items by index. Negative counts from end. Slice with [start:end]"},
            {"title": "List Methods", "code": "nums = [3, 1, 4, 1, 5]\nnums.append(9)     # [3,1,4,1,5,9]\nnums.sort()        # [1,1,3,4,5,9]\nnums.pop()         # removes 9\nprint(nums.count(1)) # 2", "explanation": "Lists have built-in methods for common operations"}
        ],
        "common_mistakes": ["Index out of range", "Confusing append with extend", "Modifying while iterating"],
        "prerequisites": ["variables"], "next_steps": ["list_comprehensions", "tuples"],
        "related_concepts": ["tuples", "comprehensions", "indexing"]
    }},
    "string": {"beginner": {
        "definition": "A string is a sequence of characters enclosed in quotes.",
        "explanation": "Strings store text. Create them with single quotes, double quotes, or triple quotes for multi-line. Python strings are immutable (can't change characters in place).",
        "key_points": ["Text data type", "Immutable (can't modify in place)", "Supports indexing and slicing", "Lots of built-in methods"],
        "analogies": ["Like beads on a string", "Like characters in a sentence", "Like a chain of letters"],
        "code_examples": [
            {"title": "String Operations", "code": "text = \"Hello, Python!\"\nprint(len(text))      # 14\nprint(text.upper())   # HELLO, PYTHON!\nprint(text.lower())   # hello, python!\nprint(text.replace(\"Python\", \"World\"))", "explanation": "Strings have many useful methods"},
            {"title": "String Formatting", "code": "name = \"Alice\"\nage = 25\n# f-strings (Python 3.6+)\nprint(f\"{name} is {age} years old\")\n# .format() method\nprint(\"{} is {} years old\".format(name, age))\n# % formatting\nprint(\"%s is %d years old\" % (name, age))", "explanation": "f-strings are the modern way to format strings"},
            {"title": "String Slicing", "code": "s = \"Python Programming\"\nprint(s[0:6])    # Python\nprint(s[7:])     # Programming\nprint(s[::-1])   # gnimmargorP nohtyP (reversed)", "explanation": "Slice strings like lists: [start:end:step]"}
        ],
        "common_mistakes": ["Trying to modify immutable strings", "Forgetting quotes", "Escape sequence issues"],
        "prerequisites": ["variables"], "next_steps": ["regex", "string_formatting"],
        "related_concepts": ["lists", "formatting", "encoding"]
    }},
    "dictionary": {"beginner": {
        "definition": "A dictionary stores key-value pairs in curly braces.",
        "explanation": "Unlike lists (which are indexed by position), dictionaries are indexed by keys. Keys must be unique and immutable (strings, numbers). Values can be anything.",
        "key_points": ["Key-value pairs", "Keys must be unique and immutable", "Fast lookups by key", "Mutable"],
        "analogies": ["Like a real dictionary (word → definition)", "Like a phonebook (name → number)", "Like a locker with labels"],
        "code_examples": [
            {"title": "Creating Dictionaries", "code": "student = {\n    \"name\": \"Alice\",\n    \"age\": 25,\n    \"courses\": [\"Python\", \"Math\"]\n}\nprint(student[\"name\"])        # Alice\nprint(student.get(\"grade\", \"N/A\"))  # N/A (safe access)", "explanation": "Access values by key. Use .get() to avoid KeyError"},
            {"title": "Dictionary Methods", "code": "d = {\"a\": 1, \"b\": 2, \"c\": 3}\nprint(d.keys())    # dict_keys(['a', 'b', 'c'])\nprint(d.values())  # dict_values([1, 2, 3])\nprint(d.items())   # dict_items([('a',1), ('b',2), ('c',3)])\nd[\"d\"] = 4        # add new key\nprint(d)", "explanation": "Dictionaries have powerful iteration methods"},
            {"title": "Dictionary Loop", "code": "student = {\"name\": \"Alice\", \"age\": 25, \"grade\": \"A\"}\nfor key, value in student.items():\n    print(f\"{key}: {value}\")", "explanation": "Iterate over key-value pairs with .items()"}
        ],
        "common_mistakes": ["Accessing missing key (use .get())", "Using mutable keys (lists)", "Forgetting keys must be unique"],
        "prerequisites": ["variables", "lists"], "next_steps": ["dict_comprehensions", "defaultdict"],
        "related_concepts": ["sets", "json", "data_structures"]
    }},
    "class": {"beginner": {
        "definition": "A class is a blueprint for creating objects with attributes and methods.",
        "explanation": "Classes enable Object-Oriented Programming. Define a class once, then create multiple instances (objects) from it. Each instance has its own data but shares the methods.",
        "key_points": ["Blueprint for objects", "Encapsulates data (attributes) and behavior (methods)", "__init__ initializes new instances", "self refers to the instance"],
        "analogies": ["Like a blueprint for a house", "Like a cookie cutter and cookies", "Like a template for a document"],
        "code_examples": [
            {"title": "Basic Class", "code": "class Student:\n    def __init__(self, name, grade):\n        self.name = name\n        self.grade = grade\n    \n    def introduce(self):\n        return f\"Hi, I'm {self.name} and I got {self.grade}\"\n\nalice = Student(\"Alice\", \"A\")\nprint(alice.introduce())  # Hi, I'm Alice and I got A", "explanation": "__init__ runs when creating a new Student. Methods take self as first parameter"},
            {"title": "Class Attributes", "code": "class Circle:\n    pi = 3.14159  # class attribute (shared)\n    \n    def __init__(self, radius):\n        self.radius = radius  # instance attribute\n    \n    def area(self):\n        return Circle.pi * self.radius ** 2\n\nc = Circle(5)\nprint(f\"Area: {c.area():.2f}\")  # Area: 78.54", "explanation": "Class attributes are shared. Instance attributes are per-object."},
            {"title": "Inheritance", "code": "class Animal:\n    def __init__(self, name):\n        self.name = name\n    def speak(self):\n        pass\n\nclass Dog(Animal):\n    def speak(self):\n        return f\"{self.name} says Woof!\"\n\nclass Cat(Animal):\n    def speak(self):\n        return f\"{self.name} says Meow!\"\n\nprint(Dog(\"Rex\").speak())\nprint(Cat(\"Luna\").speak())", "explanation": "Inheritance lets child classes reuse and override parent behavior"}
        ],
        "common_mistakes": ["Forgetting self parameter", "Confusing class/instance attributes", "Not calling super().__init__"],
        "prerequisites": ["functions", "variables"], "next_steps": ["inheritance", "magic_methods", "decorators"],
        "related_concepts": ["oop", "objects", "inheritance", "polymorphism"]
    }},
    "module": {"beginner": {
        "definition": "A module is a .py file containing reusable Python code that can be imported.",
        "explanation": "Modules help organize code into separate files. Import them with the `import` statement. Python has hundreds of built-in modules (math, os, json, etc.) and you can create your own.",
        "key_points": ["Any .py file is a module", "import statement loads modules", "from ... import ... for specific items", "Built-in modules: math, os, sys, json, random"],
        "analogies": ["Like a library section", "Like a toolbox you open when needed", "Like app plugins"],
        "code_examples": [
            {"title": "Importing Modules", "code": "import math\nimport random\nfrom datetime import datetime\n\nprint(math.sqrt(16))        # 4.0\nprint(random.randint(1,10)) # random number\nprint(datetime.now())       # current time", "explanation": "import gives access to all functions. from ... import gets specific items."},
            {"title": "Creating a Module", "code": "# Save as: mymodule.py\n# def greet(name):\n#     return f\"Hello {name}!\"\n# \n# PI = 3.14159\n\n# In another file:\n# import mymodule\n# print(mymodule.greet(\"Alice\"))  # Hello Alice!\n# print(mymodule.PI)              # 3.14159", "explanation": "Any .py file is automatically a module. Import it by filename (without .py)"}
        ],
        "common_mistakes": ["Circular imports", "Module name conflicts", "Forgetting to install third-party packages"],
        "prerequisites": ["functions"], "next_steps": ["packages", "pip", "virtual_environments"],
        "related_concepts": ["packages", "import", "namespace"]
    }},
    "exception": {"beginner": {
        "definition": "An exception is an error that occurs during program execution, which can be caught and handled.",
        "explanation": "When Python encounters an error, it raises an exception. If not handled, the program crashes. Use try/except blocks to catch and handle exceptions gracefully.",
        "key_points": ["try block contains risky code", "except block handles the error", "finally block runs regardless", "raise lets you trigger exceptions"],
        "analogies": ["Like a safety net", "Like an airbag in a car", "Like a circuit breaker"],
        "code_examples": [
            {"title": "Try/Except", "code": "try:\n    number = int(input(\"Enter a number: \"))\n    result = 10 / number\n    print(f\"Result: {result}\")\nexcept ValueError:\n    print(\"That's not a valid number!\")\nexcept ZeroDivisionError:\n    print(\"Can't divide by zero!\")\nelse:\n    print(\"No errors occurred!\")\nfinally:\n    print(\"This always runs.\")", "explanation": "Handle specific exceptions separately. else runs on success. finally always runs."},
            {"title": "Raising Exceptions", "code": "def withdraw(balance, amount):\n    if amount > balance:\n        raise ValueError(f\"Insufficient funds! Have ${balance}\")\n    return balance - amount\n\ntry:\n    new_balance = withdraw(100, 150)\nexcept ValueError as e:\n    print(f\"Error: {e}\")", "explanation": "Use raise to trigger exceptions when something goes wrong."}
        ],
        "common_mistakes": ["Bare except (catches everything)", "Swallowing exceptions silently", "Not specifying exception type"],
        "prerequisites": ["conditionals"], "next_steps": ["custom_exceptions", "logging"],
        "related_concepts": ["debugging", "logging", "error_handling"]
    }},
    "file_io": {"beginner": {
        "definition": "File I/O (Input/Output) lets your program read from and write to files on disk.",
        "explanation": "Use open() to get a file object, then read() or write(). Always close the file when done — or use the with statement which auto-closes.",
        "key_points": ["open() returns a file object", "with statement auto-closes", "Modes: 'r' read, 'w' write, 'a' append", "Always close files or use with"],
        "analogies": ["Like opening and closing a notebook", "Like a filing cabinet"],
        "code_examples": [
            {"title": "Writing and Reading", "code": "# Writing to a file\nwith open(\"notes.txt\", \"w\") as f:\n    f.write(\"Hello, file!\\n\")\n    f.write(\"Line 2\\n\")\n\n# Reading from a file\nwith open(\"notes.txt\", \"r\") as f:\n    content = f.read()\n    print(content)\n\n# Reading line by line\nwith open(\"notes.txt\", \"r\") as f:\n    for line in f:\n        print(f\"Line: {line.strip()}\")", "explanation": "The with statement ensures the file closes even if errors occur."},
            {"title": "File Modes", "code": "# Different file modes\n# \"r\"  - read (default)\n# \"w\"  - write (overwrites existing!)\n# \"a\"  - append\n# \"r+\" - read and write\n# \"rb\" - read binary\n\nwith open(\"data.json\", \"w\") as f:\n    import json\n    json.dump({\"name\": \"Alice\", \"score\": 95}, f)\n\nwith open(\"data.json\", \"r\") as f:\n    data = json.load(f)\n    print(data[\"name\"])  # Alice", "explanation": "Common patterns: JSON files for data, text files for logs, binary for images."}
        ],
        "common_mistakes": ["Forgetting to close files", "Writing in read mode", "Not handling FileNotFoundError"],
        "prerequisites": ["strings", "exception"], "next_steps": ["context_managers", "csv", "pickle"],
        "related_concepts": ["json", "os_module", "pathlib"]
    }},
    "lambda": {"beginner": {
        "definition": "A lambda is a small, anonymous function defined inline with lambda arguments: expression.",
        "explanation": "Lambdas are one-line functions without a name. Useful for short operations where defining a full function feels excessive, like callbacks in sorted(), map(), filter().",
        "key_points": ["Anonymous one-line function", "lambda args: expression", "Limited to a single expression", "Used with sorted, map, filter, reduce"],
        "analogies": ["Like a sticky note instead of a full document", "Like a quick calculator shortcut"],
        "code_examples": [
            {"title": "Lambda Basics", "code": "square = lambda x: x ** 2\ndouble = lambda x: x * 2\nadd = lambda a, b: a + b\n\nprint(square(5))     # 25\nprint(double(10))    # 20\nprint(add(3, 7))     # 10", "explanation": "lambda creates a function in one line. Assign to variable or use directly."},
            {"title": "Lambda with sorted()", "code": "students = [\n    {\"name\": \"Alice\", \"grade\": 85},\n    {\"name\": \"Bob\", \"grade\": 92},\n    {\"name\": \"Charlie\", \"grade\": 78}\n]\n# Sort by grade (highest first)\nsorted_students = sorted(students, key=lambda s: s[\"grade\"], reverse=True)\nfor s in sorted_students:\n    print(f\"{s['name']}: {s['grade']}\")", "explanation": "lambda provides a quick key function without a separate def."},
            {"title": "Lambda with filter/map", "code": "numbers = [1, 2, 3, 4, 5, 6, 7, 8]\n# Filter even numbers\nevens = list(filter(lambda x: x % 2 == 0, numbers))\n# Square all numbers\nsquares = list(map(lambda x: x ** 2, numbers))\n\nprint(f\"Evens: {evens}\")\nprint(f\"Squares: {squares}\")", "explanation": "filter() keeps items where lambda returns True. map() transforms each item."}
        ],
        "common_mistakes": ["Trying to use statements (not expressions)", "Making lambdas too complex", "Overusing when def is clearer"],
        "prerequisites": ["functions"], "next_steps": ["map_filter_reduce", "comprehensions"],
        "related_concepts": ["functions", "comprehensions", "functional"]
    }},
    "comprehensions": {"beginner": {
        "definition": "A comprehension is a concise way to create lists, dicts, or sets from iterables.",
        "explanation": "Comprehensions replace for-loop patterns with a single readable expression. [expression for item in iterable if condition] — they're faster and more Pythonic.",
        "key_points": ["List comprehension: [expr for x in iterable]", "Dict comprehension: {k:v for x in iterable}", "Set comprehension: {expr for x in iterable}", "Optional if condition filters items"],
        "analogies": ["Like a factory conveyor belt", "Like a formula that generates a collection"],
        "code_examples": [
            {"title": "List Comprehensions", "code": "# Traditional way\nsquares = []\nfor i in range(10):\n    squares.append(i ** 2)\n\n# Comprehension (Pythonic way)\nsquares = [i ** 2 for i in range(10)]\nprint(squares)  # [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]\n\n# With condition\neven_squares = [i ** 2 for i in range(10) if i % 2 == 0]\nprint(even_squares)  # [0, 4, 16, 36, 64]", "explanation": "Comprehensions are cleaner and faster than manual loops"},
            {"title": "Dict & Set Comprehensions", "code": "# Dict comprehension\nnames = [\"Alice\", \"Bob\", \"Charlie\"]\nname_lengths = {name: len(name) for name in names}\nprint(name_lengths)  # {'Alice': 5, 'Bob': 3, 'Charlie': 7}\n\n# Set comprehension (unique values)\nnums = [1, 2, 2, 3, 3, 3, 4]\nunique_squares = {x ** 2 for x in nums}\nprint(unique_squares)  # {1, 4, 9, 16}", "explanation": "Dict comprehensions and set comprehensions use {}. Sets deduplicate."},
            {"title": "Nested Comprehensions", "code": "# Flatten a matrix\nmatrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]\nflat = [num for row in matrix for num in row]\nprint(flat)  # [1, 2, 3, 4, 5, 6, 7, 8, 9]\n\n# Create multiplication table\ntable = [[i * j for j in range(1, 6)] for i in range(1, 6)]\nfor row in table:\n    print(row)", "explanation": "Nested comprehensions work like nested for loops, read left to right."}
        ],
        "common_mistakes": ["Making them too complex (use for-loops instead)", "Forgetting brackets for list vs generator"],
        "prerequisites": ["lists", "loops"], "next_steps": ["generators", "iterators"],
        "related_concepts": ["lambda", "map_filter", "generators"]
    }},
    "decorator": {"beginner": {
        "definition": "A decorator is a function that modifies the behavior of another function.",
        "explanation": "Decorators wrap a function to add functionality before/after it runs. Common uses: logging, timing, authentication, caching. Use @decorator syntax above a function.",
        "key_points": ["@decorator is syntactic sugar", "Wraps function to add behavior", "Arguments pass through via *args, **kwargs", "Common: @staticmethod, @classmethod, @property"],
        "analogies": ["Like gift wrapping", "Like adding accessories to an outfit", "Like a security guard at a door"],
        "code_examples": [
            {"title": "Simple Decorator", "code": "def timer(func):\n    def wrapper(*args, **kwargs):\n        import time\n        start = time.time()\n        result = func(*args, **kwargs)\n        end = time.time()\n        print(f\"{func.__name__} took {end-start:.3f}s\")\n        return result\n    return wrapper\n\n@timer\ndef slow_function():\n    import time\n    time.sleep(1)\n    return \"Done!\"\n\nprint(slow_function())  # slow_function took 1.001s\n                        # Done!", "explanation": "The decorator @timer wraps slow_function to time its execution."},
            {"title": "Built-in Decorators", "code": "class MyClass:\n    class_var = 0\n    \n    @classmethod\n    def from_string(cls, data):\n        # Creates instance from string\n        return cls()\n    \n    @staticmethod\n    def helper():\n        # Utility function, no self/cls needed\n        return \"Static method called\"\n    \n    @property\n    def computed(self):\n        # Accessed like an attribute, not method\n        return 42\n\nobj = MyClass()\nprint(obj.computed)  # 42 (no parentheses needed)", "explanation": "Property, classmethod, staticmethod are built-in decorators that change behavior."}
        ],
        "common_mistakes": ["Forgetting @wraps (loses function metadata)", "Decorator arguments vs no arguments confusion"],
        "prerequisites": ["functions"], "next_steps": ["context_managers", "metaclasses"],
        "related_concepts": ["functions", "closures", "wraps"]
    }},
    "recursion": {"beginner": {
        "definition": "Recursion is when a function calls itself to solve a problem by breaking it into smaller pieces.",
        "explanation": "A recursive function has two parts: base case (stops recursion) and recursive case (calls itself). Each call works on a smaller version of the problem until reaching the base case.",
        "key_points": ["Function calls itself", "Must have a base case to stop", "Each call reduces problem size", "Can cause stack overflow if too deep"],
        "analogies": ["Like Russian nesting dolls", "Like a staircase going down level by level", "Like a chain reaction"],
        "code_examples": [
            {"title": "Factorial", "code": "def factorial(n):\n    # Base case\n    if n <= 1:\n        return 1\n    # Recursive case\n    return n * factorial(n - 1)\n\nprint(factorial(5))  # 120 (5*4*3*2*1)\n\n# Trace:\n# factorial(5) = 5 * factorial(4)\n#            = 5 * 4 * factorial(3)\n#            = 5 * 4 * 3 * factorial(2)\n#            = 5 * 4 * 3 * 2 * factorial(1)\n#            = 5 * 4 * 3 * 2 * 1", "explanation": "Each call reduces n by 1 until reaching the base case of n ≤ 1."},
            {"title": "Fibonacci", "code": "def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n - 1) + fibonacci(n - 2)\n\n# Print first 10 Fibonacci numbers\nfor i in range(10):\n    print(fibonacci(i), end=\" \")  # 0 1 1 2 3 5 8 13 21 34", "explanation": "Each Fibonacci number is the sum of the two before it."},
            {"title": "Directory Tree", "code": "import os\n\ndef print_tree(path, indent=\"\"):\n    items = os.listdir(path)\n    for item in items:\n        full = os.path.join(path, item)\n        print(f\"{indent}├── {item}\")\n        if os.path.isdir(full):\n            print_tree(full, indent + \"│   \")\n\nprint_tree(\".\")", "explanation": "Recursion naturally handles nested structures like file trees."}
        ],
        "common_mistakes": ["Missing base case (infinite recursion)", "Stack overflow on large inputs", "Not making progress toward base case"],
        "prerequisites": ["functions", "loops"], "next_steps": ["memoization", "dynamic_programming"],
        "related_concepts": ["loops", "stack", "divide_conquer"]
    }},
}


class ConceptService:
    """Service for generating concept explanations"""
    
    def get_explanation(self, concept: str, level: DifficultyLevel, context: str = None) -> Dict:
        concept_lower = concept.lower().strip()
        
        # Check knowledge base first
        if concept_lower in CONCEPT_KNOWLEDGE:
            level_data = CONCEPT_KNOWLEDGE[concept_lower].get(level.value, 
                            CONCEPT_KNOWLEDGE[concept_lower].get("beginner", {}))
            return {
                "concept": concept, "level": level,
                "definition": level_data.get("definition", ""),
                "explanation": level_data.get("explanation", ""),
                "key_points": level_data.get("key_points", []),
                "analogies": level_data.get("analogies", []),
                "code_examples": level_data.get("code_examples", []),
                "common_mistakes": level_data.get("common_mistakes", []),
                "related_concepts": level_data.get("related_concepts", []),
                "prerequisites": level_data.get("prerequisites", []),
                "next_steps": level_data.get("next_steps", []),
                "estimated_reading_time_minutes": 10
            }
        
        return {"concept": concept, "level": level, "use_llm": True}


concept_service = ConceptService()


# ============================================
# API Endpoints
# ============================================

@app.post("/explain", response_model=ExplainResponse)
async def explain_concept(
    request: ExplainRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Explain a Python concept at the specified difficulty level"""
    
    student_id = current_user.get("sub") or request.student_id
    
    # Check cache
    cache_key = f"explain:{request.concept}:{request.level.value}"
    cached = await cache_get(f"explain:{request.concept}:{request.level.value}")
    if cached:
        logger.info(f"Cache hit for concept: {request.concept}")
        explanation = ConceptExplanation(**cached)
        return ExplainResponse(
            explanation=explanation,
            follow_up_suggestions=[],
            related_topics=[]
        )
    
    # Get static KB data as fallback
    fallback_data = concept_service.get_explanation(
        request.concept, request.level, request.context
    )
    
    # ALWAYS try LLM first for every concept (dynamic AI explanations)
    explanation_data = None
    llm_url = os.getenv("LLM_URL", "http://localhost:8010")
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            llm_resp = await client.post(f"{llm_url}/explain", json={
                "concept": request.concept, "level": request.level.value,
                "context": request.context,
            })
            if llm_resp.status_code == 200:
                llm_data = llm_resp.json()
                explanation_data = {
                    "concept": llm_data.get("concept", request.concept),
                    "level": request.level.value,
                    "definition": llm_data.get("definition", ""),
                    "explanation": llm_data.get("explanation", ""),
                    "key_points": llm_data.get("key_points", []),
                    "analogies": llm_data.get("analogies", []),
                    "code_examples": [{"title": e["title"], "code": e["code"], "explanation": e["explanation"], "language": "python"} for e in llm_data.get("code_examples", [])],
                    "common_mistakes": llm_data.get("common_mistakes", []),
                    "related_concepts": llm_data.get("related_concepts", []),
                    "practice_exercises": [],
                    "prerequisites": [],
                    "next_steps": llm_data.get("related_concepts", [])[:2],
                    "estimated_reading_time_minutes": 10,
                    "_source": "llm",
                }
                logger.info(f"LLM generated explanation for: {request.concept}")
    except Exception as e:
        logger.warning(f"LLM call failed, using static fallback: {e}")
    
    # Use LLM data if available, otherwise fall back to static KB
    if not explanation_data:
        explanation_data = fallback_data
        explanation_data["_source"] = explanation_data.get("_source", "static")
    
    source = explanation_data.get("_source", "static")
    explanation = ConceptExplanation(
        concept=explanation_data.get("concept", request.concept),
        level=request.level,
        definition=explanation_data.get("definition", ""),
        explanation=explanation_data.get("explanation", ""),
        key_points=explanation_data.get("key_points", []),
        analogies=explanation_data.get("analogies", []),
        code_examples=[CodeExample(**ex) for ex in explanation_data.get("code_examples", []) if ex.get("title")],
        common_mistakes=explanation_data.get("common_mistakes", []),
        related_concepts=explanation_data.get("related_concepts", []),
        practice_exercises=[],
        prerequisites=[],
        next_steps=explanation_data.get("next_steps", []),
        estimated_reading_time_minutes=explanation_data.get("estimated_reading_time_minutes", 10),
        metadata={"student_id": student_id, "source": source, "generated_at": datetime.now(timezone.utc).isoformat()}
    )
    
    # Cache result
    await cache_set(f"explain:{request.concept}:{request.level.value}", explanation.model_dump(), 3600)
    
    # Generate follow-up suggestions
    follow_up = [
        f"Practice exercises for {request.concept}",
        f"Related concept: {explanation_data.get('related_concepts', ['next_topic'])[0]}",
        f"Try exercises for {request.concept}"
    ]
    
    related = explanation_data.get("related_concepts", [])
    
    # Publish event
    background_tasks.add_task(
        publish_event,
        "concept.explained",
        "concept_explained",
        {
            "student_id": current_user.get("sub"),
            "concept": request.concept,
            "level": request.level.value,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )
    
    return ExplainResponse(
        explanation=ConceptExplanation(**explanation_data),
        follow_up_suggestions=[],
        related_topics=[]
    )


@app.get("/concepts/list")
async def list_concepts(
    level: Optional[DifficultyLevel] = None,
    current_user: dict = Depends(get_current_user)
):
    """List available concepts in the knowledge base"""
    concepts = []
    for concept, levels in CONCEPT_KNOWLEDGE.items():
        if level is None or level.value in levels:
            concepts.append({
                "name": concept,
                "available_levels": list(levels.keys()),
                "prerequisites": levels.get("beginner", {}).get("prerequisites", []),
                "next_steps": levels.get("beginner", {}).get("next_steps", [])
            })
    
    return {"concepts": concepts, "total": len(concepts)}


@app.get("/concepts/{concept}/levels")
async def get_concept_levels(
    concept: str,
    current_user: dict = Depends(get_current_user)
):
    """Get available difficulty levels for a concept"""
    concept_lower = concept.lower()
    if concept_lower not in CONCEPT_KNOWLEDGE:
        raise HTTPException(status_code=404, detail="Concept not found")
    
    return {
        "concept": concept,
        "available_levels": list(CONCEPT_KNOWLEDGE[concept_lower].keys())
    }


@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(
        status="healthy",
        service="concepts-agent",
        checks={"database": True, "redis": True, "dapr": True}
    )


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)