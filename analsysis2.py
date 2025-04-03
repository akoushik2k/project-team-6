import json
import pandas as pd

# Load the scraped issues JSON
with open("poetry.json", "r", encoding="utf-8") as f:
    issues = json.load(f)

summary_rows = []

for issue in issues:
    issue_number = issue.get("number")
    title = issue.get("title", "")
    creator = issue.get("creator")
    assignees = issue.get("assignees", [])
    events = issue.get("events", [])

    # Set of all contributors
    contributors_set = set()
    event_contributors_set = set()
    event_types_set = set()

    if creator:
        contributors_set.add(creator)
    contributors_set.update(assignees)

    for event in events:
        if isinstance(event, dict):
            event_type = event.get("event")
            event_types_set.add(event_type)

            actor = event.get("actor", {})
            if isinstance(actor, dict):
                login = actor.get("login")
                if login:
                    contributors_set.add(login)
                    event_contributors_set.add(login)

    summary_rows.append({
        "issue_number": issue_number,
        "title": title,
        "total_contributors_involved": len(contributors_set),
        "contributors_involved": ", ".join(sorted(contributors_set)),
        "event_types": ", ".join(sorted(event_types_set)),
        "event_contributors": ", ".join(sorted(event_contributors_set))
    })

# Convert to DataFrame
df_summary = pd.DataFrame(summary_rows)

# Save to Excel
df_summary.to_excel("issue_summary.xlsx", index=False)
print("✅ File 'issue_summary.xlsx' created with 1 row per issue.")
