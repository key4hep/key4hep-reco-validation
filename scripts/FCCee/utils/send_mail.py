import argparse
import smtplib
from email.message import EmailMessage

def send_mail(sender, receiver, subject, body, server):

  # Create a text/plain message
  msg = EmailMessage()
  msg.set_content(body)
  
  msg['Subject'] = subject
  msg['From'] = sender
  msg['To'] = receiver
  
  # Send the message via a SMTP server.
  s = smtplib.SMTP(server)
  s.send_message(msg)
  s.quit()


if __name__ == "__main__":
  parser = argparse.ArgumentParser(
        description="Process simulation"
    )
  parser.add_argument('-b', '--Body',  type=str, 
                      help='Body of the email', default='')
  parser.add_argument('-f', '--inputFile', type=str,
                      help='File to read to set the body of the email (has precedence on mail_body arg)', default='')
  parser.add_argument('-s', '--Subject', type=str, 
                      help='Subject of the email', default='./')
  parser.add_argument('--From', type=str, 
                      help='email address of the sender')
  parser.add_argument('--To', type=str, 
                      help='email address of the receiver')
  parser.add_argument('--Server',type=str, 
                      help='SMTP server to use', default='cernmx.cern.ch')
  
  args = parser.parse_args()
    
  if args.inputFile:
    with open(args.inputFile, 'r') as file:
      args.Body = file.read()
  send_mail(args.From, args.To, args.Subject, args.Body, args.Server)
  
  