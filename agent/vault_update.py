from dotenv import load_dotenv
load_dotenv()

import os
import subprocess
import tempfile
from github import Github
from claude_client import ask_claude
from github_client import get_pr_diff, get_pull_request

github_token = os.environ.get("GITHUB_TOKEN", "")
if not github_token:
    raise ValueError("GITHUB_TOKEN is not set.")

github = Github(github_token)


def read_vault_file(file_path: str) -> str:
    """Read a file from the vault."""
    if not os.path.exists(file_path):
        return f"File not found: {file_path}"
    with open(file_path , "r") as f:
        return f.read()


def update_vault_file(file_path: str, content: str) -> None:
    """Write updated content to a vault file."""
    with open(file_path, "w") as f:
        f.write(content)


def get_updated_project_file(
    current_content: str,
    pr_diff: str,
    pr_title: str,
    pr_body: str,
) -> str:
    """
    Ask Claude to update the project file based on what changed in the PR.
    Returns the full updated file content.
    """
    system_prompt = """You are maintaining a knowledge vault for a software project.
You will be given the current project file and a merged pull request.
Your job is to update the project file to reflect what changed.

Rules:
- Update "Problems solved" if the PR fixed a bug or resolved an issue.
- Update "Decisions made" if the PR introduced a new pattern or architectural choice.
- Update "Open items" if any items were completed or new ones emerged.
- Update "Conventions" if new conventions were introduced.
- Do NOT add noise — only update what actually changed.
- Do NOT remove existing content unless it is now wrong.
- Return the COMPLETE updated file, not just the changes.
- Keep the same markdown structure and format as the original.
"""

    user_message = f"""Here is the current project file:

{current_content}

Here is the merged pull request:

Title: {pr_title}
Description: {pr_body or 'No description provided.'}

Code changes:
{pr_diff}

Return the complete updated project file.
"""

    return ask_claude(system_prompt, user_message)


def open_vault_pr(
    vault_repo_name: str,
    file_path_in_vault: str,
    updated_content: str,
    pr_title: str,
    source_pr_number: int,
    source_repo: str,
) -> str:
    """
    Open a PR on the vault repo with the updated project file.
    Returns the URL of the created PR.
    """
    vault_repo = github.get_repo(vault_repo_name)

    # Create a new branch on the vault repo
    branch_name = f"update/pr-{source_pr_number}-from-{source_repo.split('/')[-1]}"

    # Get the current main branch SHA to branch from
    main_branch = vault_repo.get_branch("main")
    main_sha = main_branch.commit.sha

    # Create the new branch
    vault_repo.create_git_ref(
        ref=f"refs/heads/{branch_name}",
        sha=main_sha
    )

    # Get the current file to update it (need its SHA for the API)
    current_file = vault_repo.get_contents(file_path_in_vault, ref="main")

    # Update the file on the new branch
    vault_repo.update_file(
        path=file_path_in_vault,
        message=f"update: reflect changes from {source_repo}#{source_pr_number}",
        content=updated_content,
        sha=current_file.sha,
        branch=branch_name,
    )

    # Open the PR
    vault_pr = vault_repo.create_pull(
        title=f"Vault update from {source_repo}#{source_pr_number}: {pr_title}",
        body=f"Auto-generated update based on merged PR {source_repo}#{source_pr_number}.\n\nReview the changes and merge to update the vault.",
        head=branch_name,
        base="main",
    )

    return vault_pr.html_url


def run_vault_update(
    source_repo: str,
    pr_number: int,
    vault_repo: str,
    vault_file_path: str,
    current_vault_content: str,
) -> None:
    """
    Full pipeline: read merged PR → update vault file → open PR on vault.
    """
    print(f"Reading merged PR #{pr_number} from {source_repo}...")
    pr = get_pull_request(source_repo, pr_number)
    pr_diff = get_pr_diff(source_repo, pr_number)

    print("Asking Claude to update the vault file...")
    updated_content = get_updated_project_file(
        current_content=current_vault_content,
        pr_diff=pr_diff,
        pr_title=pr.title,
        pr_body=pr.body or "",
    )

    print(f"Opening PR on vault repo {vault_repo}...")
    vault_pr_url = open_vault_pr(
        vault_repo_name=vault_repo,
        file_path_in_vault=vault_file_path,
        updated_content=updated_content,
        pr_title=pr.title,
        source_pr_number=pr_number,
        source_repo=source_repo,
    )

    print(f"Vault PR opened: {vault_pr_url}")


if __name__ == "__main__":
    source_repo = os.environ.get("REPO_NAME", "NuriaOlivares/claude-agent")
    pr_number = int(os.environ.get("PR_NUMBER", "1"))
    vault_repo = os.environ.get("VAULT_REPO", "NuriaOlivares/my-vault")
    vault_file = os.environ.get("VAULT_FILE", "30_projects/claude-agent.md")
    vault_path = os.environ.get(
        "VAULT_PATH",
        os.path.expanduser("~/my-vault")
    )

    vault_file_full_path = os.path.join(vault_path, vault_file)
    current_content = read_vault_file(vault_file_full_path)

    run_vault_update(
        source_repo=source_repo,
        pr_number=pr_number,
        vault_repo=vault_repo,
        vault_file_path=vault_file,
        current_vault_content=current_content,
    )