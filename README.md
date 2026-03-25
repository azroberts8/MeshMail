# Mesh Mail

A mail system that runs over [Meshtastic](https://meshtastic.org/) networks. Interact with the service by sending slash commands as text messages to a Meshtastic node running this software.

## How it works

A host device (e.g. Raspberry Pi) connects to a Meshtastic radio over serial. The software listens for incoming direct messages and processes them as commands. User accounts are secured with TOTP (time-based one-time passwords) — on registration, users receive a secret key to add to any authenticator app (Google Authenticator, Authy, etc.), which they then use to log in.

Messages are stored locally and can be sent to any registered user.

## Commands

| Command | Description |
|---|---|
| `/help` | Show available commands |
| `/register <username>` | Create an account (returns a TOTP secret) |
| `/login <username> <otp_code>` | Log in with your authenticator code |
| `/logout` | Log out |
| `/whoami` | Show current user |
| `/sendmail <recipient> <message>` | Send mail to a registered user |
| `/inbox` | View received mail |
| `/sent` | View sent mail |

## Setup

Requires Python 3.12+ and a Meshtastic device connected via serial.

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Running

Connect a meshtastic device over serial then run:

```bash
python src/main.py
```

The service will connect to the first available Meshtastic serial device and begin listening for direct messages. The SQLite database (`mesh_mail.db`) is created automatically on first run.

## Project Structure

```
src/
├── main.py        # Entry point, command dispatch
├── commands.py    # Command implementations
├── interfaces.py  # Meshtastic messaging abstraction
├── session.py     # Session and auth management (TOTP)
└── db.py          # SQLite database initialization
```
