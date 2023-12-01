"""
commit.py: 通过几个步骤完成提交。

具体步骤包含：
1. 获取当前修改文件列表；
2. 获取用户选中的修改文件；
    a. 标记出已经staged的文件；
    b. 获取用户选中的文件；
    c. 根据用户选中文件，重新构建stage列表；
3. 获取用户选中修改文件的Diff信息；
4. 生成提交信息；
5. 展示提交信息并提交。

注意： 步骤2.c, 步骤5有专门的函数实现，本脚本中不需要具体这两个步骤的实现。
"""

import os
import sys
import time
import re
import json
import subprocess
import openai

from prompts import \
    PROMPT_SUMMARY_FOR_FILES, \
    PROMPT_GROUP_FILES, \
    PROMPT_COMMIT_MESSAGE_BY_DIFF_USER_INPUT, \
    PROMPT_COMMIT_MESSAGE_BY_SUMMARY_USER_INPUT, \
    PROMPT_SUMMARY_FOR_FILES_RETRY, \
    PROMPT_GROUP_FILES_RETRY, \
    prompt_summary_for_files_llm_config, \
    prompt_group_files_llm_config, \
    prompt_commit_message_by_diff_user_input_llm_config, \
    prompt_commit_message_by_summary_user_input_llm_config
    


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
    
    import ymal
    data = yaml.safe_load(lines[1:-1])
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
            if line.strip().startswith('``` '):
                lines = []
            elif line.strip().startswith('```'):
                lines.append(line)
                break
            lines.append(line)
        except EOFError:
            pass

    replay_message = '\n'.join(lines)
    return parse_response_from_ui(replay_message)


def call_gpt_with_config(messages, llm_config) -> str:
    connection_error = ''
    for _1 in range(3):
        try:
            response = openai.ChatCompletion.create(
                messages=messages,
                **llm_config,
                stream=False
            )
            
            response_dict = json.loads(str(response))
            respose_message = response_dict["choices"][0]["message"]
            return respose_message
        except ConnectionError as err:
            connection_error = err
            continue
        except Exception as err:
            print("Exception:", err, file=sys.stderr, flush=True)
            return None
    print("Connect Error:", connection_error, file=sys.stderr, flush=True)
    return None

def call_gpt_with_config_and_ensure_json(messages, llm_config):
    for _1 in range(3):
        response = call_gpt_with_config(messages, llm_config)
        if response is None:
            sys.exit(-1)

        try:
            response_obj = json.loads(response["content"])
            return response_obj
        except Exception:
            continue
    print("Not valid json response:", response["content"], file=sys.stderr, flush=True)
    sys.exit(-1)


def get_modified_files():
    """ 获取当前修改文件列表以及已经staged的文件列表"""
    output = subprocess.check_output(["git", "status", "-s", "-u"])
    output = output.decode('utf-8')
    lines = output.split('\n')
    modified_files = []
    staged_files = []
    
    def strip_file_name(file_name):
        file = file_name.strip()
        if file.startswith('"'):
            file = file[1:-1]
        return file

    for line in lines:
        if len(line) > 2:
            status, filename = line[:2], line[3:]
            # check wether filename is a directory
            if os.path.isdir(filename):
                continue
            modified_files.append(strip_file_name(filename))
            if status == "M " or status == "A ":
                staged_files.append(strip_file_name(filename))
    return modified_files, staged_files

def gpt_file_summary(diff, diff_files):
    prompt = PROMPT_SUMMARY_FOR_FILES.replace("{__DIFF__}", f"{diff}")
    messages = [{"role": "user", "content": prompt}]
    normpath_summaries = {}
    
    retry_times = 0
    while retry_times < 3:
        retry_times += 1
        file_summaries = call_gpt_with_config_and_ensure_json(messages, prompt_summary_for_files_llm_config)
        for key, value in file_summaries.items():
            normpath_summaries[os.path.normpath(key)] = value
        
        missed_files = [file for file in diff_files if file not in normpath_summaries]
        if len(missed_files) > 0:
            prompt_retry = PROMPT_SUMMARY_FOR_FILES_RETRY.replace("{__MISSED_FILES__}", f"{missed_files}")
            messages.append({"role": "assistant", "content": json.dumps(file_summaries)})
            messages.append({"role": "user", "content": prompt_retry})
        else:
            break
    
    return normpath_summaries


def gpt_file_group(diff, diff_files):
    prompt = PROMPT_GROUP_FILES.replace("{__DIFF__}", f"{diff}")
    messages = [{"role": "user", "content": prompt}]
    file_groups = []
    
    retry_times = 0
    while retry_times < 3:
        retry_times += 1
        file_groups = call_gpt_with_config_and_ensure_json(messages, prompt_group_files_llm_config)
        grouped_files = []
        for group in file_groups:
            grouped_files.extend(group["files"])
        missed_files = [file for file in diff_files if file not in grouped_files]
        
        if len(missed_files) > 0:
            prompt_retry = PROMPT_GROUP_FILES_RETRY.replace("{__MISSED_FILES__}", f"{missed_files}")
            messages.append({"role": "assistant", "content": json.dumps(file_groups)})
            messages.append({"role": "user", "content": prompt_retry})
        else:
            break
    
    return file_groups


def get_file_summary(modified_files, staged_files):
    """ 当modified_files文件列表<=5时，根据项目修改差异生成每一个文件的修改总结 """
    diffs = []
    for file in modified_files:
        if file not in staged_files:
            subprocess.check_output(["git", "add", file])
        diff = subprocess.check_output(["git", "diff", "--cached", file])
        if file not in staged_files:
            subprocess.check_output(["git", "reset", file])
        diffs.append(diff.decode('utf-8'))
    # total_diff = subprocess.check_output(["git", "diff", "HEAD"])
    total_diff_decoded = '\n'.join(diffs) #  total_diff.decode('utf-8')
    
    if len(total_diff_decoded) > 15000:
        print("Current diff length:", len(total_diff_decoded), flush=True)
        return {}

    # 在prompt中明确处置AI模型的输出格式需求
    normpath_summaries = gpt_file_summary(total_diff_decoded, modified_files)
    print(f"""
``` file summary
{json.dumps(normpath_summaries, indent=4)}
```
    """)

    # 通过AI模型对提交文件进行分组，分组的依据是按修改内容的关联性。
    file_groups = gpt_file_group(total_diff_decoded, modified_files)
    print(f"""
``` group
{json.dumps(file_groups, indent=4)}
```
    """)

    return normpath_summaries


def get_marked_files(modified_files, staged_files, file_summaries):
    """ 获取用户选中的修改文件及已经staged的文件"""
    # Coordinate with user interface to let user select files.
    # assuming user_files is a list of filenames selected by user.
    out_str = "```chatmark\n"
    out_str += "Staged:\n"
    for file in staged_files:
        out_str += f"- [x] {file} {file_summaries.get(file, '')}\n"
    out_str += "Unstaged:\n"
    for file in modified_files:
        if file in staged_files:
            continue
        out_str += f"- [] {file} {file_summaries.get(file, '')}\n"
    out_str += "```"
    
    output_message(out_str)
    return [file for file in modified_files if file_summaries.get(file, None)]
    replay_object = pipe_interaction_mock(out_str)
    
    select_files = []
    for key, value in replay_object.items():
        if key in modified_files and value == "true":
            select_files.append(key)
    return select_files


def rebuild_stage_list(user_files):
    """ 根据用户选中文件，重新构建stage列表 """
    # Unstage all files
    subprocess.check_output(["git", "reset"])
    # Stage all user_files
    for file in user_files:
        os.system(f"git add \"{file}\"")


def get_diff():
    """ 获取staged files的Diff信息 """
    return subprocess.check_output(["git", "diff", "--cached"])

def generate_commit_message_base_diff(user_input, diff):
    """ Based on the diff information, generate a commit message through AI """
    prompt = PROMPT_COMMIT_MESSAGE_BY_DIFF_USER_INPUT.replace(
        "{__DIFF__}", f"{diff}"
    ).replace(
        "{__USER_INPUT__}", f"{user_input}"
    )
    messages = [{"role": "user", "content": prompt}]
    response = call_gpt_with_config(messages, prompt_commit_message_by_diff_user_input_llm_config)
    return response


def generate_commit_message_base_file_summaries(user_input, file_summaries):
    """ Based on the file_summaries, generate a commit message through AI """
    prompt = PROMPT_COMMIT_MESSAGE_BY_SUMMARY_USER_INPUT.replace(
        "{__USER_INPUT__}", f"{user_input}"
    ).replace(
        "{__FILE_SUMMARY__}", f"{json.dumps(file_summaries, indent=4)}"
    )
    # Call AI model to generate commit message
    messages = [{"role": "user", "content": prompt}]
    response = call_gpt_with_config(messages, prompt_commit_message_by_summary_user_input_llm_config)
    return response


def display_commit_message_and_commit(commit_message):
    """ 展示提交信息并提交 """
    commit_message_with_flag = f"""
```editor
{commit_message}
```
    """
    replay_object = pipe_interaction_mock(commit_message_with_flag)
    new_commit_message, commit = replay_object["commit_message"], replay_object["commit"]

    if commit == "true":
        subprocess.check_output(["git", "commit", "-m", new_commit_message])


def main():
    try:
        user_input = sys.argv[1]

        modified_files, staged_files = get_modified_files()
        file_summaries = get_file_summary(modified_files, staged_files)
        selected_files = get_marked_files(modified_files, staged_files, file_summaries)
        rebuild_stage_list(selected_files)
        diff = get_diff()
        commit_message = generate_commit_message_base_diff(user_input, diff)
        commit_message2 = generate_commit_message_base_file_summaries(user_input, file_summaries)
        display_commit_message_and_commit(commit_message2["content"] + "\n\n\n" + commit_message["content"])
        output_message("""\n```progress\n\nDone\n\n```""")
        sys.exit(0)
    except Exception as err:
        print("Exception:", err, file=sys.stderr, flush=True)
        sys.exit(-1)
        
if __name__ == '__main__':
    main()
