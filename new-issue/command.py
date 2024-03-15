import sys
import os
import json

from devchat.llm.chat import chat_json
from github import Github
from github import Auth
# from common_util import editor

def read_config():
  config_path = os.path.join(os.getcwd(), '.devchat', 'information', 'config', 'config.json')
  if not os.path.exists(config_path):
    print('Config file does not exist')
    return None
  with open(config_path, 'r') as f:
    return json.load(f)

def write_config(repo_path, github_token):
  config_path = os.path.join(os.getcwd(), '.devchat', 'information', 'config', 'config.json')
  with open(config_path, 'w') as f:
    json.dump({'repo_path': repo_path, 'github_token': github_token}, f)

PROMPT= prompt = """
pls return a JSON object without line break(the response must be parsed as json, not contain any redundant chars), including a string field Title and a markdown string field called Body.
{information}
{request}
{context}
"""
@chat_json(prompt=PROMPT)
def get_issue_content(information, request, context):
  pass

PROMPT= prompt = """
I will request you to write an issue. The request is consists of two parts, Firstly, I will give a context list(organized by concept name). You may choose most related ones and return it as a json object(with key files) according to the requst content. Then I will ask you for issue content with the context you chosen. Now is the first request, pls only return an json object with context files you chosen. context files: {context_list}, issue content:
`{request_content}`
"""
@chat_json(prompt=PROMPT)
def get_related_context_file(context_list, request_content):
  pass

# @editor("Please specify the issue's repository, "
#         "If the issue is within this repository, no need to specify. "
#         "Otherwise, format as: username/repository-name")
# @editor("Input your github TOKEN to access github api:")
# def set_config(repo_path, github_token):
#   pass

def get_request(path):
  if not os.path.exists(path):
      return
  with open(path, 'r') as f:
    request = f.read()
  return request

def read_api_config():
  config = read_config()
  # set config by devlake ui
  # repo_path = ''
  # github_token = ''
  # if config != None:
  #   repo_path = config['repo_path']
  #   github_token = config['github_token']
  # else:
  #   # request user config
  #   repo_path, github_token = set_config(repo_path, github_token)

  # write_config(repo_path, github_token)
  repo_path = config['repo_path']
  github_token = config['github_token']
  return repo_path, github_token
def create_github_issue(github_token, repo_path, issue_content, issue_title):
  auth = Auth.Token(github_token)
  g = Github(auth=auth)
  repo = g.get_repo(repo_path)
  issue = repo.create_issue(title=issue_title, body=issue_content)
  print(issue, flush=True)

def main():
  # get user input
  user_input = sys.argv[1]
  params = user_input.strip().split(' ')
  user_content = params[1]
  print(f'reading request...\n', flush=True)
  request_path = os.path.join(os.getcwd(), params[0])
  request = get_request(request_path)
  if request == '':
    print('Request file does not exist', flush=True)
    return
  # get repository context
  information = ''
  # get request context
  print(f'reading context list\n', flush=True)
  # get context list
  context_list = os.listdir(os.path.join(os.getcwd(), '.devchat', 'information', 'context'))
  # print(context_list, flush=True)
  print(f'[ai]choosing context files...\n', flush=True)
  response = get_related_context_file(context_list=context_list, request_content=request + user_content)
  print(response)
  chosen_context_files = response['files']
  print(f'chosen context files: {chosen_context_files}\n', flush=True)
  print(f'reading context...\n', flush=True)
  for context_file in chosen_context_files:
    context_file_path = os.path.join(os.getcwd(), '.devchat', 'information', 'context', context_file)
    if not os.path.exists(context_file_path):
      print(f'context file {context_file} does not exist\n', flush=True)
      return
    with open(context_file_path, 'r') as f:
      information += f.read()
  print(f'context read\n', flush=True)

  print(f'reading config...\n', flush=True)
  # check if github token is configured
  repo_path, github_token = read_api_config()
  print(f'[ai] generating issue content...\n', flush=True)
  # # debug
  # print(information)
  # print(request)
  # print(user_content)
  # get issue_content from ai
  issue_content=get_issue_content(information=information, request=request, context=user_content)
  # print issue content and wait for user confirmation
  print(issue_content, flush=True)
  # TODO:: add user confirmation
  print(f'creating issue...\n', flush=True)
  create_github_issue(github_token, repo_path, issue_content['Body'], issue_content['Title'])

  # request github api to create issue
  print(f'issue created\n', flush=True)
  

if __name__ == "__main__":
  main()