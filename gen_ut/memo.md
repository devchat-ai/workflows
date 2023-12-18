
```
/test /Users/kagami/Projects/merico/chat,help me write test cases for find_refeerence_tests function in chat/ask_codebase/assistants/find_reference_tests.py,find_reference_tests,chat/ask_codebase/assistants/find_reference_tests.py
```

```
/test /Users/kagami/Projects/merico/chat,help me write test cases for propose_tests function in chat/ask_codebase/assistants/propose_tests.py,propose_tests,chat/ask_codebase/assistants/propose_tests.py
```


1. Use openai lib to make LLM calls with timeout & retry & token management
2. Upgrade models to turbo and use JSON mode if possible
3. Handle context size for directory-sturcture-based assistants

```
"help me write test cases for propose_tests function" -fn propose_tests -fp chat/ask_codebase/assistants/propose_tests.py
```
```
"help me write test cases for propose_tests function" -fn propose_tests -fp /Users/kagami/Projects/merico/chat/chat/ask_codebase/assistants/propose_tests.py
```

