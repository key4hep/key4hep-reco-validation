'''
Helper script to assist with sending status email from Key4hep Reco validation.
'''

import argparse
import sys
import smtplib
from email.message import EmailMessage


def send_mail(sender, receiver, subject, body, server):
    """
    Send the email
    """

    # Create a text/plain message
    msg = EmailMessage()
    msg.set_content(body)

    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = receiver

    # Send the message using SMTP
    smtp = smtplib.SMTP(server)
    smtp.send_message(msg)
    smtp.quit()


def main():
    """
    Parse command line arguments and set things in motion.
    """
    parser = argparse.ArgumentParser(
        description="Send Key4hep validation emails"
    )
    parser.add_argument(
        "-b", "--body",
        type=str,
        default=None,
        help="Body of the email (has precedence over --input-file argument)"
    )
    parser.add_argument(
        "-f",
        "--input-file",
        type=str,
        default=None,
        help="File containing the body of the email"
    )
    parser.add_argument(
        "-s", "--subject",
        type=str,
        default="./",
        help="Subject of the email"
    )
    parser.add_argument(
        "--from",
        type=str,
        default="key4hep-reco-validation@cern.ch",
        help="email address of the sender"
    )
    parser.add_argument(
        "--to",
        type=str,
        help="email addresses of the receivers"
    )
    parser.add_argument(
        "--server",
        type=str,
        default="cernmx.cern.ch",
        help="Email server to use"
    )

    args = parser.parse_args()

    if args.body is None:
        if args.inputFile is not None:
            with open(args.inputFile, "r", encoding="utf-8") as infile:
                args.body = infile.read()

    if args.body is None:
        print('ERROR: Please provide the text of the email.')
        print('       Using either --body or --intput-file argument')
        print('       Aborting...')
        sys.exit(1)

    send_mail(args['from'], args.to, args.subject, args.body, args.server)


if __name__ == "__main__":
    main()
