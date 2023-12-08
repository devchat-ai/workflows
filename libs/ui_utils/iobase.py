import os
import time

import yaml

def output_message(output):
    out_data = f"""\n{output}\n"""
    print(out_data, flush=True)


def parse_response_from_ui(response):
    # resonse text like this:
    """
    ``` some_name
    some key name 1: value1
    some key name 2: value2
    ```
    """
    # parse key values
    lines = response.strip().split("\n")
    if len(lines) <= 2:
        return {}

    data = yaml.safe_load('\n'.join(lines[1:-1]))
    return data


def pipe_interaction_mock(output: str):
    output_message(output)
    # read response.txt in same dir with current script file
    response_file = os.path.join(os.path.dirname(__file__), 'response.txt')
    
    # clear content in response_file
    with open(response_file, 'w+', encoding="utf8"):
        pass

    while True:
        if os.path.exists(response_file):
            with open(response_file, encoding="utf8") as f:
                response = f.read()
                if response.strip().endswith("```"):
                    break
        time.sleep(1)
    return parse_response_from_ui(response)


def pipe_interaction(output: str):
    output_message(output)

    lines = []
    while True:
        try:
            line = input()
            if line.strip().startswith('```yaml'):
                lines = []
            elif line.strip() == '```':
                lines.append(line)
                break
            lines.append(line)
        except EOFError:
            pass

    replay_message = '\n'.join(lines)
    return parse_response_from_ui(replay_message)
