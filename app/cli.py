from app import app
import os
import click

@app.cli.group()
def translate():
    """Translation and localization commands."""
    pass

@translate.command()
def update():
    """Update all languages."""
    if os.system('pybabel extract -F babel.cfg -k _l -o messages.pot .'):
        raise RuntimeError('Extract command failed')
    if os.system('pybabel update -i messages.pot -d app/translations'):
        raise RuntimeError('Update command failed')
    os.remove('messages.pot')

@translate.command()
def compile():
    """Compile all languages."""
    if os.system('pybabel compile -d app/translations'):
        raise RuntimeError('compile command failed')

@translate.command()
@click.argument('lang')
def init(lang):
    """Init a language."""
    if os.system('pybabel extract -F babel.cfg -k _l -o messages.pot .'):
        raise RuntimeError('Extract command failed')
    if os.system('pybabel init -i messages.pot -d app/translations -l'+ lang):
        raise RuntimeError('Init command failed')
    os.remove('messages.pot')