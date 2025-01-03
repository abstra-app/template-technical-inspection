import abstra.forms as af
from abstra.tasks import send_task, get_tasks
from abstra.common import get_persistent_dir
from uuid import uuid4
from PIL import Image
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
print(tasks)

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

# Fill anomalies for each scope
anomaly_types = [
    "Longitudinal crack",
    "Transverse crack",
    "Infiltration",
    "Fragmentation",
    "Wear",
    "Loss of adhesion",
]

item_anomaly = (
    af.ListItemSchema()
    .read_dropdown("Type:", options=anomaly_types, key="type", required=True)
    .read("Location:", key="location", required=True)
    .read_image("Image:", key="image", required=True)
)

inspected_scopes = []

for scope in task["scope"]:

    @af.reactive
    def render(p):
        p.display_markdown(f"## Scope: {scope}")
        anomalies_present = p.read_multiple_choice(
            "Was any anomaly found?",
            key="anomaly_present",
            options=[
                {"label": "Yes", "value": True},
                {"label": "No", "value": False},
            ],
            initial_value=False,
            required=True,
        )

        if anomalies_present:
            p.read_list(item_anomaly, min=1, key="anomalies_found")

    inspection = render.run()

    inspected = {
        "scope": scope,
        "anomaly_present": inspection["anomaly_present"],
        "anomalies_found": [],
    }

    # Save images
    if inspection["anomaly_present"]:
        for anomaly in inspection["anomalies_found"]:
            file_name = f"{str(uuid4())}.png"
            file_path = anomalies_folder / file_name
            file_obj = anomaly["image"].file

            image = Image.open(file_obj)
            image.save(file_path, "png")

            inspected["anomalies_found"].append(
                {
                    "type": anomaly["type"],
                    "location": anomaly["location"],
                    "file": file_name,
                }
            )

    inspected_scopes.append(inspected)

# Send task
payload = task.get_payload()
payload["inspected_scopes"] = inspected_scopes
send_task(
    "inspection_completed",
    payload,
)

# Finalize
task.complete()
