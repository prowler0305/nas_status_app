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
        self.config_mapper = dict()
        self._create_config_mapper()
        self._container_status_config(self.config_mapper)

    def _create_config_mapper(self):
        """
        Sets the keys and values in the class attribute dictionary to be used in the _container_status_config() method
        :return: None
        """

        self.config_mapper[os.environ.get('container_status_config_path')] = os.environ.get('container_status_path')
        self.config_mapper[os.environ.get('faq_data_config_path')] = os.environ.get('faq_data_path')

    def _container_status_config(self, config_mapper_dict):
        """
        Takes any JSON file in the config map and sets the persistent storage file.

        :param config_mapper_dict: Dictionary container config map(read only file) location to persistent(read-write)
        location
        :return:
        """

        file_path_error_message = "Path {} doesn't exist."

        for config_map_file_path, persistent_storage_path in config_mapper_dict.items():
            if os.path.exists(config_map_file_path):
                if os.path.exists(persistent_storage_path):
                    copied_to = copyfile(src=config_map_file_path, dst=persistent_storage_path)
                    container_status_app.logger.info("Source file {} copied to {}.".format(config_map_file_path, copied_to))
                else:
                    container_status_app.logger.error(file_path_error_message.format(persistent_storage_path))
            else:
                container_status_app.logger.error(file_path_error_message.format(config_map_file_path))

        return
