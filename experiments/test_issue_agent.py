from agent.issue.issue_understanding import (
    IssueUnderstandingAgent
)


agent = IssueUnderstandingAgent()


result = agent.understand(
    "The application crashes when discount is None."
)


print("\n========== ISSUE TASK ==========\n")

print(
    "Issue:"
)

print(
    result.issue_description
)

print("\nGoals:")

for goal in result.goals:
    print(f"  - {goal}")

print("\nSuspected Files:")

for file in result.suspected_files:
    print(f"  - {file}")