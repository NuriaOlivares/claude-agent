from dotenv import load_dotenv
load_dotenv()

import os
from claude_client import ask_claude
from github_client import get_pr_diff, get_pr_description, post_pr_comment


def read_vault_file(file_path: str) -> str:
    """
    Read a file from the vault.

    file_path: absolute path to the vault file,
               like /Users/yourname/my-vault/30_projects/claude-agent.md
    """
    if not os.path.exists(file_path):
        return f"Vault file not found: {file_path}"

    with open(file_path, "r") as f:
        return f.read()


def review_pull_request(
    repo_name: str,
    pr_number: int,
    vault_project_file: str,
    vault_claude_md: str,
    ) -> str:
    """
    Full pipeline: read vault + read PR + ask Claude + post comment.

    repo_name: full GitHub repo name, like "yourusername/claude-agent"
    pr_number: the PR number to review
    vault_project_file: path to the relevant project file in the vault
    vault_claude_md: path to CLAUDE.md in the vault
    """

    # Step 1 — read the vault files
    print("Reading vault files...")
    project_context = read_vault_file(vault_project_file)
    rules = read_vault_file(vault_claude_md)

    # Step 2 — read the PR from GitHub
    print(f"Reading PR #{pr_number} from {repo_name}...")
    pr_description = get_pr_description(repo_name, pr_number)
    pr_diff = get_pr_diff(repo_name, pr_number)

    # Step 3 — build the prompt for Claude
    system_prompt = f"""You are a code reviewer for a software project.
    You have been given the project conventions and rules, and you must 
    review code strictly against them.

    Be specific. Reference line numbers or function names when pointing 
    out issues. Do not invent problems that are not there.

    If the code follows the conventions well, say so clearly.

    Format your review in clean markdown suitable for a GitHub comment.
    Start with a one-line summary, then list any issues, then list what 
    was done well.

    --- PROJECT RULES (from CLAUDE.md) ---
    {rules}

    --- PROJECT CONTEXT ---
    {project_context}
    """

    user_message = f"""Please review this pull request.

    {pr_description}

    --- CODE CHANGES ---
    {pr_diff}
    """

    # Step 4 — ask Claude
    print("Asking Claude to review...")
    review = ask_claude(system_prompt, user_message)

    # Step 5 — post the comment on GitHub
    print("Posting review comment on GitHub...")
    post_pr_comment(repo_name, pr_number, review)

    return review


# Run manually for testing
if __name__ == "__main__":
    import sys

    repo = os.environ.get("REPO_NAME", "NuriaOlivares/claude-agent")
    pr_number = int(os.environ.get("PR_NUMBER", "1"))

    vault_base = os.environ.get(
        "VAULT_PATH",
        os.path.expanduser("~/documents/projects/my-vault")
    )

    vault_project = os.path.join(vault_base, "30_projects", "claude-agent.md")
    vault_rules = os.path.join(vault_base, "CLAUDE.md")

    review = review_pull_request(
        repo_name=repo,
        pr_number=pr_number,
        vault_project_file=vault_project,
        vault_claude_md=vault_rules,
    )

    print("\n=== Review posted ===")
    print(review)