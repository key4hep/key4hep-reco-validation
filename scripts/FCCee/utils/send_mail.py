'''
Helper script to assist with sending status email from Key4hep Reco validation.
'''

import argparse
import sys
import smtplib
from email.message import EmailMessage


def send_mail(args):
    """
    Send the email
    """

    # Create a text/plain message
    msg = EmailMessage()
    msg.set_content(args.body)

    msg["Subject"] = args.subject
    msg["From"] = getattr(args, 'from')
    msg["To"] = args.to

    # Send the message using SMTP
    smtp = smtplib.SMTP(args.server)
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
        if args.input_file is not None:
            with open(args.input_file, "r", encoding="utf-8") as infile:
                args.body = infile.read()

    if args.body is None:
        print('ERROR: Please provide the text of the email.')
        print('       Using either --body or --intput-file argument')
        print('       Aborting...')
        sys.exit(1)

    send_mail(args)


if __name__ == "__main__":
    main()
