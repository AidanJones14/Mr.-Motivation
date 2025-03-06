import asyncio
import json
from email.message import EmailMessage
import aiosmtplib
import openai

# SMTP Configuration
HOST = "smtp.gmail.com"

# Carrier SMS Gateway Mapping
CARRIER_MAP = {
    "verizon": "vtext.com",
    "tmobile": "tmomail.net",
    "sprint": "messaging.sprintpcs.com",
    "at&t": "txt.att.net",
    "boost": "smsmyboostmobile.com",
    "cricket": "sms.cricketwireless.net",
    "uscellular": "email.uscc.net",
}

# OpenAI API Key
openai.api_key = "OPENAI_API_KEY"


def generate_message(prompt: str) -> str:
    """Generate a message using GPT-3.5"""
    model_name = "gpt-3.5-turbo"

    response = openai.chat.completions.create(

        model=model_name,

        messages=[{"role": "user", "content": prompt}],

    ).choices[0].message.content
    return response


async def send_email(to_email: str, email: str, pword: str, msg: str, subj: str) -> None:
    """Send an email message."""
    message = EmailMessage()
    message["From"] = email
    message["To"] = to_email
    message["Subject"] = subj
    message.set_content(msg)

    send_kws = dict(username=email, password=pword, hostname=HOST, port=587, start_tls=True)
    res = await aiosmtplib.send(message, **send_kws)

    status = "failed" if not res[1] else "succeeded"
    print(f"Email to {to_email} {status}")


async def send_txt(
    num: str, carrier: str, email: str, pword: str, msg: str, subj: str
) -> None:
    """Send a text message using email-to-SMS."""
    if carrier.lower() not in CARRIER_MAP:
        print(f"Carrier {carrier} not supported for {num}")
        return

    to_email = CARRIER_MAP[carrier.lower()]

    message = EmailMessage()
    message["From"] = email
    message["To"] = f"{num}@{to_email}"
    message["Subject"] = subj
    message.set_content(msg)

    send_kws = dict(username=email, password=pword, hostname=HOST, port=587, start_tls=True)
    res = await aiosmtplib.send(message, **send_kws)

    status = "failed" if not res[1] else "succeeded"
    print(f"Message to {num} {status}")


def load_friends_from_json(json_file: str) -> list:
    """Load friends' information from a JSON file."""
    with open(json_file, 'r') as f:
        return json.load(f)


async def main():
    _email = "aidanirish14@gmail.com"
    _pword = "GMAIL_APP_PASSWORD"  # Use an App Password

    text_prompt = "Create a very short one sentence message (160 characters or less) telling me that the most important moment is right now and to check my email. ONLY RESPOND WITH THE MESSAGE"

    friends = load_friends_from_json('sms_project/friends.json')

    print(f"Generating text message for ALL")

    generated_text_message = generate_message(text_prompt)
    print(f"Generated text message: {generated_text_message}")
    
    tasks = []
    for friend in friends:
        num = friend['phone_number']
        carrier = friend['carrier']
        prompt = friend['message_prompt']
        to_email = friend.get('email')  # Optional email field



        print(f"Generating email message for {friend['name']} ({num})...")

        generated_message = generate_message(prompt)
        print(f"Generated email message: {generated_text_message}")

        subject = "Message from Mr. Motivation"

        # Send SMS
        tasks.append(send_txt(num, carrier, _email, _pword, generated_text_message, subject))

        # Send Email if available
        if to_email:
            tasks.append(send_email(to_email, _email, _pword, generated_message, subject))

    # Run all tasks concurrently
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
