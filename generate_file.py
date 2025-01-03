from abstra.tasks import get_trigger_task, send_task
from generate_pdf_file import generate_pdf_file

task = get_trigger_task()
print(task.get_payload())

# Generate PDF
file_path = generate_pdf_file(task)


# Send task
payload = task.get_payload()
payload["file_path"] = file_path

send_task(
    "file_generated",
    payload,
)

# Finalize
task.complete()
