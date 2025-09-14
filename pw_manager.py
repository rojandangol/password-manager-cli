# ===========================
# Password Manager CLI
# ===========================
# Features:
# - Generate secure random passwords
# - Encrypt/decrypt passwords using a master password
# - Store encrypted passwords in a JSON file
# - Retrieve and list stored accounts via CLI
#
# Security:
# - Uses PBKDF2 for key derivation from a master password
# - Uses Fernet (AES-128-CBC + HMAC) for encryption
#
# Author: Rojan Dangol + AI
# ===========================

import secrets
import string
import json
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from base64 import urlsafe_b64encode
import click
import pyperclip

# File used to store encrypted account entries
STORAGE_FILE = 'storage.json'


# ---------------------------
# Password Generation
# ---------------------------
def generate_password(length=12, uppercase=True, digits=True, symbols=True):
    """
    Generate a secure random password.
    
    Args:
        length (int): Password length (default 12).
        uppercase (bool): Include uppercase letters.
        digits (bool): Include numbers.
        symbols (bool): Include punctuation characters.
    
    Returns:
        str: Generated password.
    """
    chars = string.ascii_lowercase
    if uppercase:
        chars += string.ascii_uppercase
    if digits:
        chars += string.digits
    if symbols:
        chars += string.punctuation
    return ''.join(secrets.choice(chars) for _ in range(length))


# ---------------------------
# Encryption / Decryption
# ---------------------------
def generate_key(master_password, salt=b"pw-manager-salt"):
    """
    Derive a symmetric key from a master password using PBKDF2-HMAC-SHA256.
    
    Args:
        master_password (str): User's master password.
        salt (bytes): Random salt (default is static for now).
    
    Returns:
        bytes: Base64-encoded 32-byte key.
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = urlsafe_b64encode(kdf.derive(master_password.encode()))
    return key


def encrypt_password(key, password):
    """
    Encrypt a password using Fernet symmetric encryption.
    
    Args:
        key (bytes): Encryption key derived from master password.
        password (str): Plaintext password to encrypt.
    
    Returns:
        str: Encrypted password token (base64-encoded).
    """
    f = Fernet(key)
    return f.encrypt(password.encode()).decode()


def decrypt_password(key, token):
    """
    Decrypt a password token using Fernet.
    
    Args:
        key (bytes): Encryption key derived from master password.
        token (str): Encrypted password token.
    
    Returns:
        str: Decrypted plaintext password.
    """
    f = Fernet(key)
    return f.decrypt(token.encode()).decode()


# ---------------------------
# Storage (JSON file)
# ---------------------------
def load_storage():
    """
    Load encrypted password storage from JSON file.
    
    Returns:
        dict: Storage data (accounts dictionary).
    """
    if not os.path.exists(STORAGE_FILE):
        return {"accounts": {}}
    with open(STORAGE_FILE, "r") as f:
        return json.load(f)
    

def save_storage(data):
    """
    Save storage dictionary to JSON file.
    
    Args:
        data (dict): Storage data to write.
    """
    with open(STORAGE_FILE, "w") as f:
        json.dump(data, f, indent=4)


def add_entry(account, encrypted_password):
    """
    Add or update a password entry for an account.
    
    Args:
        account (str): Account name.
        encrypted_password (str): Encrypted password token.
    """
    data = load_storage()
    data["accounts"][account] = encrypted_password
    save_storage(data)


def get_entry(account):
    """
    Retrieve the encrypted password for a given account.
    
    Args:
        account (str): Account name.
    
    Returns:
        str | None: Encrypted password token if exists, else None.
    """
    data = load_storage()
    return data["accounts"].get(account)


def list_accounts():
    """
    List all accounts currently stored.
    
    Returns:
        list[str]: List of account names.
    """
    data = load_storage()
    return list(data["accounts"].keys())


# ---------------------------
# CLI Commands
# ---------------------------
def prompt_master_password():
    """
    Prompt user for their master password (hidden input).
    
    Returns:
        str: Master password input.
    """
    return click.prompt("Enter master password", hide_input=True)


@click.group()
@click.pass_context
def cli(ctx):
    """
    Password Manager CLI
    
    Commands:
        generate  Generate a secure password.
        add       Add a new encrypted password entry.
        get       Retrieve a stored password.
        list      Show all stored accounts.
    """
    # Ask for master password once and store derived key in context
    master_password = prompt_master_password()
    ctx.obj = {"key": generate_key(master_password)}


@cli.command()
@click.option('--length', default=12, help='Length of the password.')
@click.option('--uppercase/--no-uppercase', default=True)
@click.option('--digits/--no-digits', default=True)
@click.option('--symbols/--no-symbols', default=True)
def generate(length, uppercase, digits, symbols):
    """Generate a secure random password."""
    password = generate_password(length, uppercase, digits, symbols)
    click.echo(password)


@cli.command()
@click.argument('account')
@click.pass_context
def add(ctx, account):
    """Add a new password entry for ACCOUNT."""
    password = click.prompt(f"Password for {account}", hide_input=True)
    encrypted = encrypt_password(ctx.obj["key"], password)
    add_entry(account, encrypted)
    click.echo(f"Password for {account} saved.")


@cli.command()
@click.argument('account')
@click.pass_context
def get(ctx, account):
    """Retrieve stored password for ACCOUNT."""
    encrypted = get_entry(account)
    if not encrypted:
        click.echo("Account not found.")
        return
    try:
        password = decrypt_password(ctx.obj["key"], encrypted)
        # click.echo(f"Password for {account}: {password}")
        pyperclip.copy(password)
        click.echo(f"Password for {account} has been copied to clipboard ✅")

    except Exception:
        click.echo("Failed to decrypt. Wrong master password?")

def load_accounts():
    """Load and return all stored account names from JSON."""
    if not os.path.exists("storage.json"):
        return []
    with open("storage.json", "r") as f:
        data = json.load(f)
    return list(data["accounts"].keys())

@cli.command()
def listaccounts():
    """List all stored accounts."""
    accounts = load_accounts()
    click.echo("Accounts:")
    for acc in accounts:
        click.echo(f"- {acc}")

if __name__ == "__main__":
    cli()
