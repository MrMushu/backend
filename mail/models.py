from django.db import models
import email
import imaplib

# Create your models here.


def get_body(msg):
    if msg.is_multipart():
        return get_body(msg.get_payload(0))
    else:
        return msg.get_payload(None, True)


def login(user='testtest@juanpollo.com', password='Worms4mayhem$'):

    imap_url = 'imap.secureserver.net'

    con = imaplib.IMAP4_SSL(imap_url)
    con.login(user, password)
    return (con)


def get_mails(con):
    con.select('INBOX')
    unseen = con.search(None, 'UNSEEN')[1]
    seen = con.search(None, 'SEEN')[1]
    flagged = con.search(None, 'FLAGGED')[1]
    unflagged = con.search(None, 'UNFLAGGED')[1]
    emails = []

    result, mail = con.search(None, 'ALL')

    for mail in mail[0].split():

        result, data = con.fetch(mail, '(RFC822)')
        raw = email.message_from_bytes(data[0][1])

        message_id = (mail)

        mail_from = raw['From']
        email_from = mail_from[mail_from.find('<')+1:mail_from.find('>')]
        name_from = mail_from[0:mail_from.find('<')-1]

        to = [{
            'name': 'me',
            'email': raw['To']
        }]

        subject = raw['Subject']
        message = get_body(raw)
        use = str(message).replace('\\r\\n', '<br>')
        message = use[2:-1]

        time = raw['Date']

        read = mail in unseen[0].split()
        starred = mail in flagged[0].split()

        important = False
        has_attachments = False
        attachments = []
        labels = []
        folder = 0

        mails = {
            'id': message_id,
            'from': {
                'name': name_from,
                'avatar': 'assets/images/avatars/alice.jpg',
                'email': email_from
            },
            'to': to,
            'subject': subject,
            'message': message,
            'time': time,
            'read': read,
            'starred': starred,
            'important': important,
            'hasAttachments': has_attachments,
            'attachments': attachments,
            'labels': labels,
            'folder': folder

        }
        emails.insert(0, mails)

    return(emails)


def get_mail(con, mailId):
    con.select('INBOX')
    unseen = con.search(None, 'UNSEEN')[1]
    seen = con.search(None, 'SEEN')[1]
    flagged = con.search(None, 'FLAGGED')[1]
    unflagged = con.search(None, 'UNFLAGGED')[1]

    emails = []

    result, data = con.fetch(mailId[0], '(RFC822)')
    raw = email.message_from_bytes(data[0][1])

    message_id = (mailId[0])

    mail_from = raw['From']
    email_from = mail_from[mail_from.find('<')+1:mail_from.find('>')]
    name_from = mail_from[0:mail_from.find('<')-1]

    to = [{
        'name': 'me',
        'email': raw['To']
    }]

    subject = raw['Subject']
    message = get_body(raw)
    use = str(message).replace('\\r\\n', '<br>')
    message = use[2:-1]

    time = raw['Date']

    read = mailId[0] in unseen[0].split()
    starred = mailId[0] in flagged[0].split()

    important = False
    has_attachments = False
    attachments = []
    labels = []
    folder = 0

    mails = {
        'id': message_id,
        'from': {
            'name': name_from,
            'avatar': 'assets/images/avatars/alice.jpg',
            'email': email_from
        },
        'to': to,
        'subject': subject,
        'message': message,
        'time': time,
        'read': read,
        'starred': starred,
        'important': important,
        'hasAttachments': has_attachments,
        'attachments': attachments,
        'labels': labels,
        'folder': folder

    }
    emails.append(mails)
    return(mails)
