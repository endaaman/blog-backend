import json

import click
import bcrypt

@click.group()
def cli():
    pass

@cli.command()
@click.option(
    '-p',
    '--password',
    type=str,
    required=True,
)
@click.option(
    '-d',
    '--dest',
    type=str,
)
def password(password, dest):
    salt = bcrypt.gensalt(rounds=10, prefix=b'2a')
    hash_ = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    if not dest:
        print(f'hash: `{hash_}`')
        return

    with open(dest, 'w', encoding='utf-8') as f:
        f.write(hash_)
