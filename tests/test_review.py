import pytest
import os
from unittest.mock import MagicMock, patch, mock_open


def test_read_vault_file_returns_content(tmp_path):
    """
    Test that read_vault_file reads a real file correctly.
    tmp_path is a pytest built-in that gives us a temporary folder.
    No mocking needed here — reading files is simple enough to test for real.
    """
    # Create a temporary vault file
    vault_file = tmp_path / "claude-agent.md"
    vault_file.write_text("# Project: Claude Agent\n\nSome content here.")

    from review import read_vault_file
    result = read_vault_file(str(vault_file))

    assert "Claude Agent" in result
    assert "Some content here" in result


def test_read_vault_file_handles_missing_file():
    """
    Test that read_vault_file does not crash when file does not exist.
    It should return a helpful message instead.
    """
    from review import read_vault_file
    result = read_vault_file("/this/path/does/not/exist.md")

    assert "not found" in result.lower()


def test_review_pull_request_full_pipeline(mocker):
    """
    Test the full review pipeline end to end with everything mocked.
    This verifies all the pieces connect correctly without any real API calls.
    """
    # Mock vault files
    mocker.patch(
        "review.read_vault_file",
        side_effect=[
            "# Project conventions here",  # first call — project file
            "# Claude rules here",          # second call — CLAUDE.md
        ]
    )

    # Mock GitHub functions
    mocker.patch(
        "review.get_pr_description",
        return_value="Title: Fix bug\nDescription: Fixed the auth issue"
    )
    mocker.patch(
        "review.get_pr_diff",
        return_value="+def fixed_function(): pass"
    )

    # Mock Claude response
    mocker.patch(
        "review.ask_claude",
        return_value="## Good PR\n\nLooks correct."
    )

    # Mock the comment posting
    mock_post = mocker.patch("review.post_pr_comment")

    # Run the pipeline
    from review import review_pull_request
    result = review_pull_request(
        repo_name="NuriaOlivares/claude-agent",
        pr_number=1,
        vault_project_file="/fake/path/claude-agent.md",
        vault_claude_md="/fake/path/CLAUDE.md",
    )

    # Verify the review was posted
    mock_post.assert_called_once()
    assert "Good PR" in result