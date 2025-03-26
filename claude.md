Goals of these principles:
- Readability
- Testability
- Maintainability

1. Fundamentals
   1.1. Specification must match implementation
   1.2. Write functional code when possible and performance is not at stake
   1.3. No classes, except when the language forces you to (like Java)
   1.4. Immutable data structures for readability and code reuse
   1.5. Use linters and typehinting tools in dynamically typed languages

2. Variable Scope
   2.1. No global variables in functions
   2.2. Main data structures can be defined globally
   2.3. Global data structures must never be used globally

3. Architecture
   3.1. Separate private API from public API by:
        - Putting public API at the top, or
        - Separating into two files
   3.2. Have clear boundaries between core logic and I/O
