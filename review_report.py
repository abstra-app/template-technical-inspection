import abstra.forms as af
from abstra.tasks import get_tasks, send_task
from abstra.common import create_public_link, get_persistent_dir
import os
from abstra.tables import select_one

# Retrieve user data
user_email = af.get_user().email

# Folder to store images
persistent_dir = get_persistent_dir()
pdf_folder = persistent_dir / "pdf"

if not pdf_folder.exists():
    os.makedirs(pdf_folder)

# Retrieve pending requests
tasks = get_tasks()

if not tasks:
    af.display("There are no pending requests.", end_program=True)

# Select request
selection = af.read_cards(
    "Select the request you wish to attend to:",
    [
        {
            "title": f"{request['address']} - {request['zip']}",
            "subtitle": f"Engineer's Decision: {request['report']['engineer_decision']}",
            "description": request["reason"],
            "key": request.id,
        }
        for request in tasks
    ],
)

task = next(t for t in tasks if t.id == selection["key"])

# Review page
file_path = pdf_folder / task["file_path"]

try:
    file_link = create_public_link(file_path)
except Exception as e:
    print(e)
    exit(0)


@af.reactive
def render(p):
    p.display_markdown(f"## Report Review")
    p.display_link(file_link, link_text="Partial Report")
    choice = p.read_multiple_choice(
        "Reviewer's Decision:",
        ["Approved", "Rejected"],
        key="reviewer_decision",
        initial_value="Approved",
    )

    if choice == "Rejected":
        p.read_textarea("Observations:", key="observations", required=True)


result = render.run()

# Send task
payload = task.get_payload()
payload["review"] = {
    "reviewer": select_one("team_members", where={"email": user_email}),
    "reviewr_decision": result["reviewer_decision"],
    "observations": result.get("observations"),
}

if result["reviewer_decision"] == "Approved":
    send_task("report_approved", payload)
else:
    send_task("report_rejected", payload)

# Finalize
task.complete()
