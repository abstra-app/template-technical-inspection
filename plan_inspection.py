import abstra.forms as af
from abstra.tables import select
from abstra.tasks import send_task, get_tasks
from datetime import datetime, timedelta

# Retrieve user data
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
            "subtitle": ", ".join(request["scope"]),
            "description": request["reason"],
            "key": request.id,
        }
        for request in tasks
    ],
)

task = next(t for t in tasks if t.id == selection["key"])

# Inspection planning
slots = []
max_date = datetime.now() + timedelta(days=14)
current_date = datetime.now()
while current_date < max_date:
    if current_date.weekday() < 5:
        for hour in range(10, 18):
            if hour == 12:
                continue
            begin = current_date.replace(hour=hour, minute=0)
            end = begin + timedelta(minutes=45)
            slots.append((begin, end))
    current_date += timedelta(days=1)

inspector_options = [
    {"label": f"{inspector['name']} - {inspector['email']}", "value": inspector}
    for inspector in select("team_members")
]

planning_page = (
    af.Page()
    .display("Inspection Planning")
    .read_appointment("Inspection date:", slots=slots, key="date", required=True)
    .read_dropdown(
        "Inspector:", options=inspector_options, key="inspector", required=True
    )
    .run()
)

# Send task
task_payload = task.get_payload()
task_payload["plan"] = planning_page

send_task(
    "inspection_planned",
    task_payload,
)

# Finalize
task.complete()

