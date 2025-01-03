# Technical Inspection Automation
## How It Works

This project automates the process of requesting and completing technical inspections using Abstra Workflows. It allows users to request inspections, enables the company team to plan visits, collect data, generate reports, review, and send them back.

To customize this template for your team and build more, <a href="https://meet.abstra.app/demo?url=template-technical-inspection" target="_blank">book a demonstration here</a>.

![image](https://github.com/user-attachments/assets/6a81fcf4-a89c-4f17-a639-fa711d5fb1ac)

## Initial Configuration

To use this project, some initial configurations are necessary:

1. **Python Version**: Ensure Python version 3.9 or higher is installed on your system.

2. **Set Database**: To ensure the correct table schema for the project, you can follow these steps:
   1. Open your terminal and navigate to the project directory.
   2. Run the following command:

      ```sh
      abstra restore
      ```

4. **Dependencies**: To install the necessary dependencies for this project, a `requirements.txt` file is provided. This file includes all the required libraries.

   Follow these steps to install the dependencies:

   1. Open your terminal and navigate to the project directory.
   2. Run the following command to install the dependencies from `requirements.txt`:

      ```sh
      pip install -r requirements.txt
      ```
      
5. **Access Control**: The generated forms are protected by default. For local testing, no additional configuration is necessary. However, for cloud usage, you need to add your own access rules. For more information on how to configure access control, refer to the <a href="https://docs.abstra.io/concepts/access-control" target="_blank">Abstra access control documentation</a>.
 
6. **Local Usage**: To access the local editor with the project, use the following command:

   ```sh
   abstra editor path/to/your/project/folder/
   ```

## General Workflows

The following workflows automate the process of requesting, inspecting, reporting, and sending inspection reports.

### Request Inspection

Users request a technical inspection, triggering the workflow.

- **request_inspection.py**: Form for users to submit inspection requests.

### Evaluation and Planning

The team evaluates requests and plans inspections accordingly.

- **evaluate_request.py**: Form for assessing the scope and requirements of each inspection request.
- **plan_inspection.py**: Form for scheduling and organizing inspections.

### Field Data Collection

On-site data collection during the inspection visit.

- **collect_field_data.py**: Form to record data collected in the field.

### Report Generation and Review

Reports are generated from collected data and reviewed for approval.

- **fill_report.py**: Form to compile inspection data into a report.
- **review_report.py**: Form for reviewing and approving reports.

### Sending the Report

Once approved, reports are sent back to the requester.

- **send_report.py**: Script to send the finalized report to the requester.

If you're interested in customizing this template for your team, <a href="https://meet.abstra.app/demo?url=template-inspection-automation" target="_blank">book a customization session here</a>.
