import toolkit_sqlite
import config

SQLFile = 'database_deploy.sql'
with toolkit_sqlite.SqliteDB(config.DB_FILE) as db:
    db.create_database(SQLFile)