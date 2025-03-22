import subprocess
import logging
import datetime
import tempfile
from cron.init_cron import init_job
from util.config import get_config
from util.uploader import S3Uploader

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@init_job("0 22 * * *")
def database_backup_job():
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    databases_host = get_config("BACKUP_DATABASE_HOST").split(",")
    databases_port = get_config("BACKUP_DATABASE_PORT").split(",")
    databases_user = get_config("BACKUP_DATABASE_USERNAME").split(",")
    databases_password = get_config("BACKUP_DATABASE_PASSWORD").split(",")
    databases_name = get_config("BACKUP_DATABASE_NAME").split(",")

    for index, database_name in enumerate(databases_name):
        try:
            database_host = databases_host[index]
            database_port = databases_port[index]
            database_user = databases_user[index]
            database_password = databases_password[index]

            with tempfile.NamedTemporaryFile(suffix=".sql", delete=False) as temp_file:
                backup_file = temp_file.name

            additional_command = f"-p{database_password}" if database_password else ""

            command = f"mysqldump -h {database_host} -P {database_port} {additional_command} -u {database_user} {database_name} > {backup_file}"
            subprocess.run(command, shell=True, check=True)
            logger.info(f"Database backup successful: {backup_file}")

            file_name = f"{database_name}_{timestamp}.sql"
            S3Uploader().upload_file(bucket_name="database-backups",
                                     file_path=backup_file,
                                     file_name=file_name,
                                     content_type="application/sql")
        except subprocess.CalledProcessError as e:
            logger.error(f"Database backup failed for {database_name}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error for {database_name}: {e}")
        finally:
            try:
                subprocess.run(f"rm -f {backup_file}", shell=True)
            except Exception as e:
                logger.warning(f"Failed to delete temp file: {e}")
