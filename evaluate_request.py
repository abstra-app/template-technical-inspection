import abstra.forms as af
from abstra.tasks import send_task, get_tasks

# Retrieve user email
user_email = af.get_user().email

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
            "subtitle": f"Requested by {request['solicitor']['name']} - {request['solicitor']['email']}",
            "description": request["reason"],
            "key": request.id,
        }
        for request in tasks
    ],
)

task = next(t for t in tasks if t.id == selection["key"])

# Determine inspection scope
possible_scopes = [
    "Electrical installations",
    "Plumbing installations",
    "Structure",
    "Flooring",
]

scope_page = (
    af.Page()
    .display_markdown(
        f"""
### Inspection Scope\n
**Requester:** {task["solicitor"]["name"]} - {task["solicitor"]["email"]}\n
**Address:** {task["address"]} - {task["zip"]}\n
**Purpose:** {task["reason"]}
"""
    )
    .read_tag(
        "Inspection scope:",
        initial_value=possible_scopes,
        key="scope",
        required=True,
    )
    .run()
)

# Send task
task_payload = task.get_payload()
task_payload["scope"] = scope_page["scope"]

send_task(
    "scope_defined",
    task_payload,
)

# Finalize
task.complete()
