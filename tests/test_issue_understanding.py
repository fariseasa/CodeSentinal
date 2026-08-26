from agent.issue.issue_understanding import (
    IssueUnderstandingAgent
)


def test_issue_understanding():

    agent = IssueUnderstandingAgent()

    result = agent.understand(
        "The application crashes when discount is None."
    )

    assert result.issue_description

    assert len(result.goals) >= 1

    assert isinstance(
        result.suspected_files,
        list
    )