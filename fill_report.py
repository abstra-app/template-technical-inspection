import abstra.forms as af
from abstra.tasks import get_tasks, send_task
from abstra.common import get_persistent_dir
from abstra.tables import select_one
import os

# Retrieve user data
user_email = af.get_user().email

# Folder to store images
persistent_dir = get_persistent_dir()
anomalies_folder = persistent_dir / "anomalies"

if not anomalies_folder.exists():
    os.makedirs(anomalies_folder)

# Retrieve pending requests
tasks = get_tasks()

if not tasks:
    af.display("There are no pending requests.", end_program=True)

# Select request
selection = af.read_cards(
    "Select the request you wish to attend to:",
    [
        {
            "title": f"{request['address']} - {request['zip']}"
            + (" (Review)" if request.type == "report_rejected" else ""),
            "subtitle": ", ".join(request["scope"]),
            "description": request["reason"],
            "key": request.id,
        }
        for request in tasks
    ],
)

task = next(t for t in tasks if t.id == selection["key"])

# Inspected scopes
inspected_scopes_pages = []

if task.type == "report_rejected":
    review_page = (
        af.Page()
        .display_markdown("## Reviewer Observations")
        .display(task["review"]["observations"])
    )

    inspected_scopes_pages.append(review_page)

for scope in task["inspected_scopes"]:
    page = af.Page().display_markdown(f"## Scope: {scope['scope']}")

    if scope["anomalies_found"]:
        page = page.display_markdown("### Anomalies found:")

        for anomaly in scope["anomalies_found"]:
            page = page.display_markdown(
                f"**Type:** {anomaly['type']}<br>**Location:** {anomaly['location']}"
            )
            page = page.display_image(anomalies_folder / anomaly["file"])

    else:
        page = page.display_markdown("### No anomalies found.")

    inspected_scopes_pages.append(page)

# Conclusion Page
inspected_scopes_pages.append(
    af.Page()
    .display_markdown("## Fill out Report")
    .read_multiple_choice(
        "Evaluator's decision:",
        options=["Positive", "Negative"],
        initial_value="Positive",
        key="decision",
    )
    .read_textarea("Conclusion", key="conclusion", required=True)
)

steps_response = af.run_steps(inspected_scopes_pages)

# Send task
payload = task.get_payload()
payload["report"] = {
    "engineer": select_one("team_members", where={"email": user_email}),
    "engineer_decision": steps_response[-1]["decision"],
    "conclusion": steps_response[-1]["conclusion"],
}

send_task(
    "report_filled",
    payload,
)

# Finalize
task.complete()

