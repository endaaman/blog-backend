import click

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
    required=True,
)
def password(password, dest):
    print("PW", password)
    print("DEST", dest)
