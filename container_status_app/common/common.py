import os
import itertools
from flask import jsonify, flash, Response, json, current_app as container_status_app
from config import container_status_app_dir
import traceback


class Common(object):
    """
    Common class that encapsulates static methods for common functionality.

    """

    @staticmethod
    def generate_error_response(error_msg_key, error_text, response_code):
        """
        Formats a simple error message to be returned in http response as a JSON object.

        :param error_msg_key: string to use as the key in the JSON object error response returned.
        :param error_text: Message text to be returned. It will be sent as a part of a JSON response with the
        "uscc_eng_parser_api_msg" key value. (i.e. {"msg_api_msg": "<error_text>"})
        :param response_code: the HTTP response code to be set as the response.status_code
        :return: Error message and status code in a JSON format
        """

        error_response = jsonify({error_msg_key: error_text})
        error_response.status_code = response_code
        return error_response

    @staticmethod
    def check_path_exists(path):
        """
        Check if a file exists within the file structure.

        :param path: Path to the directory or file
        :return: True or False the directory or file exists
        """

        return os.path.exists(path)

    @staticmethod
    def find_file_in_project(file_name: str, path=container_status_app_dir, relative_path: bool=True):
        """
        Find a given file in the application directory tree structure and return its relative path to the root app dir.

        :param file_name:
        :param path: Path to start search top down from. Defaults to the applications root directory.
        :param relative_path: True - path to matching file is relative to :param path. False - absolute path to file.
        :return: list containing the relatives path to all occurrences of the matching file_name
        """

        dir_found = []
        for root, dirs, files in os.walk(path):
            if file_name in files:
                if relative_path:
                    dir_found.append(os.path.join(os.path.relpath(root), file_name))
                else:
                    dir_found.append(os.path.join(root, file_name))

        return dir_found

    @staticmethod
    def create_flash_message(message=None, category_request=None):
        """
        Creates a flask flash message object that can be used on the next HTTP request.

        :param message: Can be a string or an HTTP response object in which the response text which should contain the
        standard HTTP error text will be extracted as the message
        :param category_request: category of the message as documented in flask.helpers.flash()
        :return: Flash object that was created.
        """

        if isinstance(message, Response):
            if 'message' in message:
                message_dict = json.loads(message)
            else:
                message_dict = dict(message=None)
                message_dict['message'] = str(message.status_code) + ':' + message.reason
            return flash(message_dict['message'], category=category_request)
        else:
            return flash(message, category=category_request)

    @staticmethod
    def rw_json_file(file_path, mode='read', output_dict=None):
        """
        Given a path and a IO mode ("read", or "write"), either reads in a JSON and converts it to a
        dictionary or if "write" then converts the dictionary(output_dict) to JSON and writes it out to the path
        indicated in which the exists file(if there is one) is truncated.

        :param file_path: Path to a valid formatted JSON file
        :param mode: Defaults to "read", specify "write" to write out a dictionary to JSON format.
        :param output_dict: Required if "mode='write') and contains a dictionary object to be converted to JSON format.
        :return: For mode='read' -> Tuple(True/False, dictionary/None)
                 For mode='write' -> Tuple(True/False, "file_path written to")
                 For mode= invalid value -> Tuple (False, error message)
        """

        if mode == 'read':
            try:
                with open(file_path) as jsrfh:
                    dict_to_return = json.load(jsrfh)
                    return True, dict_to_return
            except FileNotFoundError:
                return False, None

        elif mode == 'write':
            try:
                with open(file_path, mode='w') as jswfh:
                    json.dump(output_dict, jswfh)
                    return True, file_path
            except Exception as err:
                container_status_app.logger.exception(err)
                return False, None
        else:
            return False, "Value for parameter 'mode' invalid. Expected 'read' or 'write'"

    @staticmethod
    def flatten_list(dict_of_lists: dict) -> list:
        """
        Give a dictionary that contains a list for each value of a key/value pair, combine and flatten all items across
        all lists into one list object.

        Note: the keys in the dictionary are not significant and can be any string value.

        Example:

            {
                "key1": "['a', 'b', 'c']"
                "key2": "['e', 'f', 'g']"
                "key3": "['h', 'i', 'j']"
            }

            returned as: ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j']

        :param dict_of_lists: A dictionary containing lists as the value in a the key/value pair
        :return: all items across all lists as a single list object
        """

        return list(itertools.chain.from_iterable(dict_of_lists.values()))
