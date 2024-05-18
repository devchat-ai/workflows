import os
import sys
import json
from typing import Optional, Tuple

from pr_agent.git_providers.git_provider import GitProvider, IncrementalPR
from pr_agent.git_providers.github_provider import GithubProvider
import pr_agent.git_providers as git_providers

from lib.chatmark import Form, TextEditor, Button

class DevChatProvider(GitProvider):
    def __init__(self, pr_url: Optional[str] = None, incremental=IncrementalPR(False)):
        # 根据某个状态，创建正确的GitProvider
        provider_type = os.environ.get('CONFIG.GIT_PROVIDER_TYPE')
        self.provider: GitProvider = git_providers._GIT_PROVIDERS[provider_type](pr_url, incremental)

    @property
    def pr(self):
        return self.provider.pr
    
    @property
    def diff_files(self):
        return self.provider.diff_files
    
    @property
    def github_client(self):
        return self.provider.github_client

    def is_supported(self, capability: str) -> bool:
        return self.provider.is_supported(capability)

    def get_diff_files(self):
        return self.provider.get_diff_files()
    
    def need_edit(self):
        button = Button(
            [
                "Commit",
                "Edit"
            ],
        )
        button.render()
        return 1 == button.clicked

    def publish_description(self, pr_title: str, pr_body: str):
        # Preview pr title and body
        print(f"\n\nPR Title: {pr_title}", end="\n\n", flush=True)
        print("PR Body:", end="\n\n", flush=True)
        print(pr_body, end="\n\n", flush=True)

        # Need Edit?
        if self.need_edit():
            # Edit pr title and body
            title_editor = TextEditor(pr_title)
            body_editor = TextEditor(pr_body)
            form = Form(['Edit pr title:', title_editor, 'Edit pr body:', body_editor])
            form.render()
            
            pr_title = title_editor.new_text
            pr_body = body_editor.new_text
        if not pr_title or not pr_body:
            print("Title or body is empty, please fill in the title and body.")
            sys.exit(0)

        return self.provider.publish_description(pr_title, pr_body)

    def publish_code_suggestions(self, code_suggestions: list) -> bool:
        code_suggestions_json_str = json.dumps(code_suggestions, indent=4)
        code_suggestions_editor = TextEditor(
            code_suggestions_json_str,
            "Edit code suggestions in JSON format:"
        )
        code_suggestions_editor.render()

        code_suggestions_json_new = code_suggestions_editor.new_text
        if not code_suggestions_json_new:
            print("Code suggestions are empty, please fill in the code suggestions.")
            sys.exit(0)
        
        code_suggestions = json.loads(code_suggestions_json_new)
        return self.provider.publish_code_suggestions(code_suggestions)

    def get_languages(self):
        return self.provider.get_languages()

    def get_pr_branch(self):
        return self.provider.get_pr_branch()
    
    def get_files(self):
        return self.provider.get_files()

    def get_user_id(self):
        return self.provider.get_user_id()

    def get_pr_description_full(self) -> str:
        return self.provider.get_pr_description_full()

    def edit_comment(self, comment, body: str):
        if body.find("## PR Code Suggestions") == -1:
            return self.provider.edit_comment(comment, body)

        print(f"\n\n{body}", end="\n\n", flush=True)

        if self.need_edit():
            comment_editor = TextEditor(
                body,
                "Edit Comment:"
            )
            comment_editor.render()

            body = comment_editor.new_text

        if not body:
            print("Comment is empty, please fill in the comment.")
            sys.exit(0)

        return self.provider.edit_comment(comment, body)

    def reply_to_comment_from_comment_id(self, comment_id: int, body: str):
        return self.provider.reply_to_comment_from_comment_id(comment_id, body)

    def get_pr_description(self, *, full: bool = True) -> str:
        return self.provider.get_pr_description(full=full)

    def get_user_description(self) -> str:
        return self.provider.get_user_description()

    def _possible_headers(self):
        return self.provider._possible_headers()

    def _is_generated_by_pr_agent(self, description_lowercase: str) -> bool:
        return self.provider._is_generated_by_pr_agent(description_lowercase)

    def get_repo_settings(self):
        return self.provider.get_repo_settings()

    def get_pr_id(self):
        return self.provider.get_pr_id()

    def get_line_link(self, relevant_file: str, relevant_line_start: int, relevant_line_end: int = None) -> str:
        return self.provider.get_line_link(relevant_file, relevant_line_start, relevant_line_end)

    #### comments operations ####
    def publish_comment(self, pr_comment: str, is_temporary: bool = False):
        if is_temporary:
            return None
        if pr_comment.find("## Generating PR code suggestions") != -1:
            return None

        if (not is_temporary and \
                pr_comment.find("## Generating PR code suggestions") == -1 and \
                pr_comment.find("**[PR Description]") == -1):
            print(f"\n\n{pr_comment}", end="\n\n", flush=True)

            if self.need_edit():
                pr_comment_editor = TextEditor(
                    pr_comment
                )
                form = Form(['Edit pr comment:', pr_comment_editor])
                form.render()
                
                pr_comment = pr_comment_editor.new_text
        if not pr_comment:
            print("Comment is empty, please fill in the comment.")
            sys.exit(0)

        return self.provider.publish_comment(pr_comment, is_temporary=is_temporary)

    def publish_persistent_comment(self, pr_comment: str,
                                   initial_header: str,
                                   update_header: bool = True,
                                   name='review',
                                   final_update_message=True):
        print(f"\n\n{initial_header}", end="\n\n", flush=True)
        print(pr_comment, end="\n\n", flush=True)

        if self.need_edit():
            pr_comment_editor = TextEditor(
                pr_comment
            )
            form = Form(['Edit pr comment:', pr_comment_editor])
            form.render()

            pr_comment = pr_comment_editor.new_text

        if not pr_comment:
            print("Comment is empty, please fill in the comment.")
            sys.exit(0)
        return self.provider.publish_persistent_comment(pr_comment, initial_header, update_header, name, final_update_message)

    def publish_inline_comment(self, body: str, relevant_file: str, relevant_line_in_file: str):
        return self.provider.publish_inline_comment(body, relevant_file, relevant_line_in_file)

    def create_inline_comment(self, body: str, relevant_file: str, relevant_line_in_file: str,
                              absolute_position: int = None):
        return self.provider.create_inline_comment(body, relevant_file, relevant_line_in_file, absolute_position)

    def publish_inline_comments(self, comments: list[dict]):
        return self.provider.publish_inline_comments(comments)

    def remove_initial_comment(self):
        return self.provider.remove_initial_comment()

    def remove_comment(self, comment):
        return self.provider.remove_comment(comment)

    def get_issue_comments(self):
        return self.provider.get_issue_comments()

    def get_comment_url(self, comment) -> str:
        return self.provider.get_comment_url(comment)

    #### labels operations ####
    def publish_labels(self, labels):
        if not os.environ.get('ENABLE_PUBLISH_LABELS', None):
            return None
        return self.provider.publish_labels(labels)

    def get_pr_labels(self, update=False):
        return self.provider.get_pr_labels(update=update)

    def get_repo_labels(self):
        return self.provider.get_repo_labels()

    def add_eyes_reaction(self, issue_comment_id: int, disable_eyes: bool = False) -> Optional[int]:
        return self.provider.add_eyes_reaction(issue_comment_id, disable_eyes=disable_eyes)

    def remove_reaction(self, issue_comment_id: int, reaction_id: int) -> bool:
        return self.provider.remove_reaction(issue_comment_id, reaction_id)

    #### commits operations ####
    def get_commit_messages(self):
        return self.provider.get_commit_messages()

    def get_pr_url(self) -> str:
        return self.provider.get_pr_url()

    def get_latest_commit_url(self) -> str:
        return self.provider.get_latest_commit_url()

    def auto_approve(self) -> bool:
        return self.provider.auto_approve()

    def calc_pr_statistics(self, pull_request_data: dict):
        return self.provider.calc_pr_statistics(pull_request_data)

    def get_num_of_files(self):
        return self.provider.get_num_of_files()
    
    @staticmethod
    def _parse_issue_url(issue_url: str) -> Tuple[str, int]:
        return GithubProvider._parse_issue_url(issue_url)
