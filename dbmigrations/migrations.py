from dbmigrations.sqlitemigrators import InitMigrator


def do_migrations(sqlite_db_path):
    # write here migrations to apply
    # APPEND ONLY
    MIGRATIONS = [
        InitMigrator(sqlite_db_path),
    ]

    last_version_available = len(MIGRATIONS) - 1
    last_version_applied = -1
    last_version_read = -1

    for n_version, migrator in enumerate(MIGRATIONS):
        if migrator.apply(n_version):
            last_version_applied = migrator.get_version()
        try:
            last_version_read = migrator.get_version()
        except:
            pass
    print("Migration summary:")
    print("*",
          f"Applied migrations up to {last_version_applied}"if last_version_applied > -1 else "No migration applied")
    print("*", f"Database version: {last_version_read} (latest available: {last_version_available})")
