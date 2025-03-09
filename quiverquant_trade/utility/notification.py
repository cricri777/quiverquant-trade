import os
from pathlib import Path

import boto3
from typing import List
import re

from jinja2 import Environment, FileSystemLoader

from utility.log import get_logger
from utility.my_quiver import CongressRepresentative

IS_NOTIFICATION_ENABLED = os.getenv("IS_NOTIFICATION_ENABLED", 'False').lower() in ('true', '1', 't')
EMAIL_LIST_NOTIFICATION = os.getenv("EMAIL_LIST_NOTIFICATION", "christian.bruneau777@gmail.com").split(",")

log = get_logger(__name__)

class Notification:
    def __init__(self,
                 data: List[CongressRepresentative],
                 ):
        self.ses_client = boto3.client('ses', region_name='ca-central-1')
        self.source_email = "christian.bruneau777@gmail.com"
        self.recipient_emails = EMAIL_LIST_NOTIFICATION
        log.debug(f"list of recipient_emails={self.recipient_emails}")
        self.data = data


    def _generate_email_body(self) -> str:
        """
        Generates an email body by populating data into an HTML utility.template.
        """
        # Locate the directory of the utility.template file
        template_dir = Path(__file__).parent / "templates"
        template_file = 'email_template.html.j2'

        # Set up Jinja2 environment
        env = Environment(loader=FileSystemLoader(template_dir))
        template = env.get_template(template_file)

        # Prepare the data to populate into the utility.template
        context = {
            "title": "Recent Congressional Trading Report (Purchase only)",
            "description": "Here are the recent congressional purchase activities:",
            "congress_representatives": [rep.get_all_fields_in_str_as_dict() for rep in self.data]
        }

        # compaction
        email_body = re.sub(r'>\s+<', '><', template.render(context))  # Removes whitespace between HTML tags
        email_body = re.sub(r'\n+', '', email_body)  # Removes line breaks
        return email_body

    def send_email_via_ses(self):
        """
        Sends the email with the generated body via AWS SES.
        """

        email_body = self._generate_email_body()  # Generate the email body
        log.debug(f"Email body: {email_body}")

        if IS_NOTIFICATION_ENABLED:
            log.debug("Sending email notification via SES")
            try:
                response = self.ses_client.send_email(
                    Source=self.source_email,  # Must be verified in SES
                    Destination={
                        'ToAddresses': self.recipient_emails  # List of email recipients
                    },
                    Message={
                        'Subject': {
                            'Data': "Notification of Recent Congressional Trading Report (Purchase only)"
                        },
                        'Body': {
                            'Html': {
                                'Data': email_body,  # HTML body
                                'Charset': 'UTF-8'
                            },
                            'Text': {
                                'Data': "Recent Congressional purchase activities. Refer to the email for details.",
                                'Charset': 'UTF-8'
                            }
                        }
                    }
                )
                log.info(f"Email sent successfully: {response}")
            except Exception as e:
                log.error(f"Failed to send email via SES: {e}")
        else:
            log.debug("Notifications are disabled. No email is sent.")