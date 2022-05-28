from django.db.migrations.executor import MigrationExecutor
from django.db import connections, DEFAULT_DB_ALIAS, ProgrammingError

def is_database_migrated(database_name):

    connection = connections[database_name]
    connection.prepare_database()
    executor = MigrationExecutor(connection)
    targets = executor.loader.graph.leaf_nodes()
    return not executor.migration_plan(targets)


def execute_initial_celery_migrations():

    from django.core import management
    management.call_command('makemigrations')
    management.call_command("migrate")


if not is_database_migrated(DEFAULT_DB_ALIAS):
    try:
        execute_initial_celery_migrations()
    except(ProgrammingError):
        logger.error('Could not apply Initial Migrations.')
        raise NotImplementedError()


