import asyncio
import re
import ssl
import smtplib
import logging
from email.message import EmailMessage
from random import randint

import aiosmtplib

from studyhelperbot import config, error_info
from studyhelperbot.db import StudyHelperBotDB

params = config("registration")
SYNC_MODE = params["sync_mode"]  # sync or async
LOCAL_MODE = bool(int(params["local_mode"]))


async def add_email_task(recipient_user_id, recipient_email):
    """Verifies an prz_email address and if it is valid creates an email coroutine"""
    if not re.match(r"^(?!.*[^\d\w]{2,}.*)[\d\w][\d\w\.\-\_]{1,30}[\d\w]@(?:stud\.)?prz\.edu\.pl$",
                    recipient_email):
        raise ValueError("The email domain is not correct and/or the email itself is impossible.")
    loop = asyncio.get_running_loop()
    email_task = loop.create_task(send_email(
        user_id=recipient_user_id,
        email_address=recipient_email,
        threshold=float(params["threshold"])
    ))
    # return verification_id
    return await email_task


async def send_email(user_id, email_address, threshold=3.0):
    """Generates an email and sends it"""
    # Throttle the speed of the email sending
    await asyncio.sleep(threshold)

    # Generate password, subject and body
    password = f"{randint(1_000, 999_999):06}"
    subject, body = create_email_subject_and_body(password)

    # Compose an email
    msg = EmailMessage()
    msg["From"] = params["sender"]
    msg["To"] = email_address
    msg["Subject"] = subject
    msg.set_content(body)

    # Send that email
    try:
        if SYNC_MODE == "async" and not LOCAL_MODE:
            await aiosmtplib.send(
                msg,
                hostname=params["hostname"],
                port=int(params["port"]),
                username=params["username"],
                password=params["password"],
                start_tls=True,
            )
        elif SYNC_MODE == "async" and LOCAL_MODE:
            await aiosmtplib.send(
                msg,
                hostname=params["local_hostname"],
                port=int(params["local_port"]),
            )
        elif SYNC_MODE == "sync" and not LOCAL_MODE:
            context = ssl.create_default_context()
            with smtplib.SMTP(params["hostname"], int(params["port"])) as smtp:
                smtp.ehlo()
                smtp.starttls(context=context)
                smtp.ehlo()
                smtp.login(params["username"], params["password"])
                smtp.send_message(msg)

        elif SYNC_MODE == "sync" and LOCAL_MODE:
            with smtplib.SMTP(params["local_hostname"], int(params["local_port"])) as smtp:
                smtp.send_message(msg)
        else:
            raise ValueError(f"Expected MODE to be 'sync' or 'async', but '{SYNC_MODE}' received.")
    except (Exception, OSError):
        logging.error(error_info())
    else:
        # This part will be executed only if there was no exceptions
        logging.info(f"handlers/registration.py:"
                     f"Password {password} was sent to "
                     f"{email_address} (user_id = {user_id}). "
                     f"Params: sm={SYNC_MODE}, local={LOCAL_MODE}.")

        # Create a record in the database
        db = AnalizaDB()
        db.connect()
        verification_id = db.create_user_verification_record(user_id, password, email_address)
        db.disconnect()
        return verification_id

    # None will be returned if there was en exception
    return None


def create_email_subject_and_body(password):
    # TODO: create a separate file with all the text messages (.ini or constants.py)
    readable_password = f"{password[:3]} {password[-3:]}"
    subject = "Telegram Analiza Bot: Email verification code"
    body, = (f"Dear client,\nyour personal verification code is the following:"
             f"\n\n{readable_password}\n\nIf you didn't asked for the code you can just "
             f"delete this email or contact the administrator.",)
    return subject, body


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    for i in range(5):
        print(asyncio.run(add_email_task(27, "166731@stud.prz.edu.pl")))
