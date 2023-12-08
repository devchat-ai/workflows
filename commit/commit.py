import os
import sys
import json
import subprocess
from typing import List

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
    

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'libs'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..' , 'libs'))

from ui_utils import ui_checkbox_select, ui_text_edit, CheckboxOption
from llm_api import chat_completion_no_stream, chat_completion_no_stream_return_json


language = ""

def assert_value(value, message):
    if value:
        print(message, file=sys.stderr, flush=True)
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

def gpt_file_summary(diff, diff_files, user_input):
    global language
    prompt = PROMPT_SUMMARY_FOR_FILES.replace("{__DIFF__}", f"{diff}").replace("{__USER_INPUT__}", f"{user_input}")
    messages = [{"role": "user", "content": prompt + (" \nPlease response summaries in chinese" if language == "chinese" else "")}]
    normpath_summaries = {}
    
    retry_times = 0
    while retry_times < 3:
        retry_times += 1
        file_summaries = chat_completion_no_stream_return_json(messages, prompt_summary_for_files_llm_config)
        if not file_summaries:
            continue
        for key, value in file_summaries.items():
            normpath_summaries[os.path.normpath(key)] = value
        
        missed_files = [file for file in diff_files if file not in normpath_summaries]
        if len(missed_files) > 0:
            prompt_retry = PROMPT_SUMMARY_FOR_FILES_RETRY.replace("{__MISSED_FILES__}", f"{missed_files}")
            messages.append({"role": "assistant", "content": json.dumps(file_summaries)})
            messages.append({"role": "user", "content": prompt_retry + (" \nPlease response summaries in chinese" if language == "chinese" else "")})
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
        file_groups = chat_completion_no_stream_return_json(messages, prompt_group_files_llm_config)
        if not file_groups:
            continue
        if 'groups' in file_groups:
            file_groups = file_groups["groups"]
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


def get_file_summaries(modified_files, staged_files, user_input):
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
        return {}, []

    # 在prompt中明确处置AI模型的输出格式需求
    normpath_summaries = gpt_file_summary(total_diff_decoded, modified_files, user_input)
    print(f"""
``` file summary
{json.dumps(normpath_summaries, indent=4)}
```
    """)

    return normpath_summaries

def get_file_summaries_and_groups(modified_files, staged_files, user_input):
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
        return {}, []

    # 在prompt中明确处置AI模型的输出格式需求
    normpath_summaries = gpt_file_summary(total_diff_decoded, modified_files, user_input)
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

    return normpath_summaries, file_groups


def get_marked_files(modified_files, staged_files, file_summaries, file_groups=None):
    """ 获取用户选中的修改文件及已经staged的文件"""
    # Coordinate with user interface to let user select files.
    # assuming user_files is a list of filenames selected by user.
    # commit_files = [] if len(file_groups) == 0 else sorted(file_groups, key=lambda obj: obj['importance_level'])[0]['files']
    options : List[CheckboxOption] = []
    options += [CheckboxOption(file, file + " - " + file_summaries.get(file, ''), "Staged", True) for file in staged_files]
    options += [CheckboxOption(file, file + " - " + file_summaries.get(file, ''), "Unstaged", False) for file in modified_files if file not in staged_files]

    selected_files = ui_checkbox_select("Select files to commit", options)
    return selected_files


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
    global language
    language_prompt = "You must response commit message in chinese。\n" if language == "chinese" else ""
    prompt = PROMPT_COMMIT_MESSAGE_BY_DIFF_USER_INPUT.replace(
        "{__DIFF__}", f"{diff}"
    ).replace(
        "{__USER_INPUT__}", f"{user_input + language_prompt}"
    )
    messages = [{"role": "user", "content": prompt}]
    response = chat_completion_no_stream(messages, prompt_commit_message_by_diff_user_input_llm_config)
    assert_value(not response, "")
    return response


def generate_commit_message_base_file_summaries(user_input, file_summaries):
    """ Based on the file_summaries, generate a commit message through AI """
    global language
    language_prompt = "Please response commit message in chinese.\n" if language == "chinese" else ""
    prompt = PROMPT_COMMIT_MESSAGE_BY_SUMMARY_USER_INPUT.replace(
        "{__USER_INPUT__}", f"{user_input}"
    ).replace(
        "{__FILE_SUMMARY__}", f"{json.dumps(file_summaries, indent=4)}"
    )
    # Call AI model to generate commit message
    messages = [{"role": "user", "content": language_prompt + prompt}]
    response = chat_completion_no_stream(messages, prompt_commit_message_by_summary_user_input_llm_config)
    assert_value(not response, "")
    return response


def display_commit_message_and_commit(commit_message):
    """ 展示提交信息并提交 """
    new_commit_message = ui_text_edit("Edit commit meesage", commit_message)
    if not new_commit_message:
        return
    subprocess.check_output(["git", "commit", "-m", new_commit_message])


def main():
    global language
    try:
        user_input = sys.argv[1]
        language = sys.argv[2]

        modified_files, staged_files = get_modified_files()
        file_summaries = get_file_summaries(modified_files, staged_files, user_input)
        # file_summaries, file_groups = get_file_summaries_and_groups(modified_files, staged_files, user_input)
        selected_files = get_marked_files(modified_files, staged_files, file_summaries)
        if len(selected_files) == 0:
            print("No files selected, commit aborted.")
            return
        rebuild_stage_list(selected_files)
        
        summaries_for_select_files = {file: file_summaries[file] for file in selected_files if file in file_summaries}
        if len(summaries_for_select_files.keys()) < len(selected_files):
            diff = get_diff()
            commit_message = generate_commit_message_base_diff(user_input, diff)
        else:
            commit_message = generate_commit_message_base_file_summaries(user_input, summaries_for_select_files)
            
        # display_commit_message_and_commit(commit_message2["content"] + "\n\n\n" + commit_message["content"])
        display_commit_message_and_commit(commit_message["content"])
        print("""\n```progress\n\nDone\n\n```""")
        sys.exit(0)
    except Exception as err:
        print("Exception:", err, file=sys.stderr, flush=True)
        sys.exit(-1)
        
if __name__ == '__main__':
    main()
