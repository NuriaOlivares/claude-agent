def format_review_comment(review: str) -> str:
    """Wrap a review in a standard markdown format for GitHub comments."""
    return f"## Claude Code Review\n\n{review}"
