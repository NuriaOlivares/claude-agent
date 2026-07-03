from dotenv import load_dotenv
load_dotenv()

import os
from github import Github
from github.PullRequest import PullRequest

github_token = os.environ.get("GITHUB_TOKEN", "")

if not github_token:
    raise ValueError("GITHUB_TOKEN is not set. Check your .env file.")

github = Github(github_token)


def get_pull_request(repo_name: str, pr_number: int) -> PullRequest:
    """
    Fetch a pull request object from GitHub.

    repo_name: the full repo name, like "yourusername/claude-agent"
    pr_number: the PR number, like 1 or 42
    """
    repo = github.get_repo(repo_name)
    return repo.get_pull(pr_number)


def get_pr_diff(repo_name: str, pr_number: int) -> str:
    """
    Get the code diff of a PR as a plain string.

    This is the actual lines of code that changed —
    lines starting with + were added, lines with - were removed.
    """
    pr = get_pull_request(repo_name, pr_number)

    diff_text = ""

    for file in pr.get_files():
        diff_text += f"\n--- File: {file.filename} ---\n"

        if file.patch:
            diff_text += file.patch
        else:
            diff_text += "(binary file or no changes)"

    return diff_text


def get_pr_description(repo_name: str, pr_number: int) -> str:
    """
    Get the title and description of a PR.
    Useful context for the code review.
    """
    pr = get_pull_request(repo_name, pr_number)

    title = pr.title
    body = pr.body or "No description provided."

    return f"Title: {title}\n\nDescription:\n{body}"


def post_pr_comment(repo_name: str, pr_number: int, comment: str) -> None:
    """
    Post a comment on a PR.
    This is how the agent delivers the code review back to GitHub.
    """
    pr = get_pull_request(repo_name, pr_number)
    pr.create_issue_comment(comment)
    print(f"Comment posted on PR #{pr_number}")


if __name__ == "__main__":
    # Replace with repo name and a real PR number
    REPO = "NuriaOlivares/claude-agent"
    PR_NUMBER = 1

    print("=== PR Description ===")
    print(get_pr_description(REPO, PR_NUMBER))

    print("\n=== PR Diff ===")
    print(get_pr_diff(REPO, PR_NUMBER))