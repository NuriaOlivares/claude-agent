import pytest
from unittest.mock import MagicMock, patch


def test_get_pr_diff_returns_string(mocker):
    """
    Test that get_pr_diff returns a string containing file diffs.
    Mocks the GitHub API so no real network call is made.
    """
    # Build a fake PR file with a patch (diff)
    fake_file = MagicMock()
    fake_file.filename = "agent/utils.py"
    fake_file.patch = "+def format_review_comment(review: str) -> str:\n+    return review"

    # Build a fake PR that returns our fake file
    fake_pr = MagicMock()
    fake_pr.get_files.return_value = [fake_file]

    # Patch the github object inside github_client
    with patch("github_client.github") as mock_github:
        mock_github.get_repo.return_value.get_pull.return_value = fake_pr

        from github_client import get_pr_diff
        result = get_pr_diff("NuriaOlivares/claude-agent", 1)

    assert "agent/utils.py" in result
    assert "format_review_comment" in result
    assert isinstance(result, str)


def test_get_pr_diff_handles_binary_files(mocker):
    """
    Test that binary files (images, etc.) do not crash the diff reader.
    Binary files have no patch — we should handle that gracefully.
    """
    fake_file = MagicMock()
    fake_file.filename = "assets/logo.png"
    fake_file.patch = None  # binary files have no patch

    fake_pr = MagicMock()
    fake_pr.get_files.return_value = [fake_file]

    with patch("github_client.github") as mock_github:
        mock_github.get_repo.return_value.get_pull.return_value = fake_pr

        from github_client import get_pr_diff
        result = get_pr_diff("NuriaOlivares/claude-agent", 1)

    # Should not crash, should mention the file
    assert "assets/logo.png" in result
    assert "binary" in result.lower()


def test_post_pr_comment_calls_github(mocker):
    """
    Test that post_pr_comment actually calls create_issue_comment
    on the correct PR. We verify the integration point, not GitHub itself.
    """
    fake_pr = MagicMock()

    with patch("github_client.github") as mock_github:
        mock_github.get_repo.return_value.get_pull.return_value = fake_pr

        from github_client import post_pr_comment
        post_pr_comment("NuriaOlivares/claude-agent", 1, "Great code!")

    # Verify create_issue_comment was called with our comment
    fake_pr.create_issue_comment.assert_called_once_with("Great code!")


def test_get_pr_description_formats_correctly(mocker):
    """
    Test that get_pr_description returns title and body in a readable format.
    """
    fake_pr = MagicMock()
    fake_pr.title = "Add utils module"
    fake_pr.body = "This adds the format_review_comment helper."

    with patch("github_client.github") as mock_github:
        mock_github.get_repo.return_value.get_pull.return_value = fake_pr

        from github_client import get_pr_description
        result = get_pr_description("NuriaOlivares/claude-agent", 1)

    assert "Add utils module" in result
    assert "format_review_comment" in result