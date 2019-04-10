import os
import json
from shutil import copyfile
from container_status_app import container_status_app


class SetConfigMaps(object):
    """
    Class that encapsulates logic to read in the config map objects and store a copy in the persistent storage location.
    This is needed since some data files used by the container_status_app are read from and written to and config map
    files are read-only, which allows any changes needed to be done to the config map file can be done without needing
    to update the persistent storage file directly.

    For example:

        The container_status_data file contains the JSON data that populates the /nas_status endpoint. If there are
        design changes that require refactoring of the JSON structure it can still be done via the CONFIG MAP object and
        on pod restart it will copy from that read only location and update the persistent storage directory location.
    """
    def __init__(self):
        self.persistent_storage_path = os.environ.get('container_status_path')
        self.config_map_path = os.environ.get('container_status_config_path')
        self._container_status_config(config_map_file_path=self.config_map_path,
                                      persistent_storage_path=self.persistent_storage_path)

    def _container_status_config(self, config_map_file_path, persistent_storage_path):
        """
        Takes the container_status_data JSON file in the config map and sets the persistent storage file.

        :param config_map_file_path: Path to the mounted read only config map file
        :param persistent_storage_path: Path to the mounted persistent storage directory
        :return:
        """

        file_path_error_message = "Environment variable {} points to path that doesn't exist."

        if os.path.exists(config_map_file_path):
            if os.path.exists(persistent_storage_path):
                copyfile(src=config_map_file_path, dst=persistent_storage_path)
                return True
            else:
                container_status_app.logger.error(file_path_error_message.format(persistent_storage_path))
                return False
        else:
            container_status_app.logger.error(file_path_error_message.format(config_map_file_path))
            return False
