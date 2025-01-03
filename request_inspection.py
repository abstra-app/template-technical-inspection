import abstra.forms as af
from abstra.tasks import send_task


# Retrieve user email
user_email = af.get_user().email


# Request inspection
personal_info = (
    af.Page()
    .display("Inspection Request")
    .read("Name:", key="name", required=True)
    .run()
)

address_info = (
    af.Page()
    .display("Inspection Request")
    .read("Address:", key="address", required=True)
    .read("ZIP Code:", key="zip", required=True)
    .read_textarea("Reason:", key="reason", required=True)
    .run()
)


# Send task
send_task(
    "inspection_requested",
    {
        "solicitor": {
            "name": personal_info["name"],
            "email": user_email,
        },
        "address": address_info["address"],
        "zip": address_info["zip"],
        "reason": address_info["reason"],
    },
)
