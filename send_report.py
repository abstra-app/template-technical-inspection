from abstra.tasks import get_trigger_task
from generate_pdf_file import generate_pdf_file
from abstra.common import create_public_link, get_persistent_dir
from abstra.messages import send_email
import os

persistent_dir = get_persistent_dir()
pdf_folder = persistent_dir / "pdf"

if not pdf_folder.exists():
    os.makedirs(pdf_folder)

# Retrieve pending tasks
task = get_trigger_task()

# Generate PDF
file_name = generate_pdf_file(task)
file_path = pdf_folder / file_name

try:
    file_link = create_public_link(file_path)
except Exception as e:
    print(e)
    exit(0)

send_email(
    to=[
        task["solicitor"]["email"],
        task["plan"]["inspector"]["email"],
    ],
    title="Technical Report",
    message="\n".join(
        [
            "The generated technical report is attached.",
            f"Download link: {file_link}",
        ]
    ),
)

task.complete()
