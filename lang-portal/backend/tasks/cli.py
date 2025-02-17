import click
from pathlib import Path
import sys

# Add the backend directory to Python path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(backend_dir))

# Change the import to use the direct path
from cmd.server import create_app

from seed_manager import SeedManager
from migration_manager import MigrationManager
from internal.models.models import db

app = create_app()

@click.group()
def cli():
    """Language Portal CLI tool"""
    pass

@cli.command()
def init_db():
    """Initialize the database"""
    with app.app_context():
        db.create_all()
        click.echo('Database initialized!')

@cli.command()
def drop_db():
    """Drop all database tables"""
    with app.app_context():
        db.drop_all()
        click.echo('Database dropped!')

@cli.command()
def migrate():
    """Run database migrations"""
    db_path = Path(__file__).parent.parent / 'db' / 'words.db'
    manager = MigrationManager(db_path)
    manager.run_migrations()

@cli.command()
@click.argument('seed_file')
@click.argument('group_name')
def seed(seed_file: str, group_name: str):
    """Seed data from a JSON file into a group"""
    db_path = Path(__file__).parent.parent / 'db' / 'words.db'
    manager = SeedManager(db_path)
    manager.seed_data(seed_file, group_name)

@cli.command(name='seed-activity')
def seed_activity():
    """Seed basic study activity"""
    db_path = Path(__file__).parent.parent / 'db' / 'words.db'
    manager = SeedManager(db_path)
    manager.seed_basic_activity()

if __name__ == '__main__':
    cli()