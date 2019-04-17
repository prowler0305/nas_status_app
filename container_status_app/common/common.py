import collections
import os
from flask import jsonify, flash, Response, json
from flask_restful import reqparse
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
    def generate_argument_dictionary(argument_name, arg_option_list=None, help_message_text=None):
        """
        Generates the dictionary needed to use the Common.create_api_parser() given the name of the argument to add and
        a list of the defining options as documented by the Class: 'Argument' constructor in flask_restful reqparse.py.

        :param argument_name: (string) The name of the argument to add. This name will be the name needed to be used on
        the HTTP request being made.
        :param arg_option_list: This should be a list of strings with the format 'arg_option=arg_value', where arg_option
        is the name of the add_argument option and arg_value is its value.

            Example: ['required=True', help='help string', etc..]

            If the option specifying can be a container then specify the arg_value as a list of comma delimated values. In
            which the value portion will be converted into a list before it is added to the dictionary for the arg_option
            key.

                E.g. - 'choices=choice1,choice2,choice3'
                arg_option - choices
                arg_value - ['choice1', 'choice2', 'choice3']

                dict = [{'choices': ['choice1', 'choice2', 'choice3'], ...


            If no arg list is given than just dictionary with argument name and value are returned.

        :return: Ordered dictionary.
        """

        # Create an ordered dictionary to fill in. This dict is ordered so that we can make it easier to use on the
        # backend when user calls Common.create_api_parser() method as the argument name will be first followed by the
        # argument options which can be in any order after that.
        arg_dict = collections.OrderedDict()

        arg_dict['arg_name'] = argument_name

        if arg_option_list is not None:
            for list_elm in arg_option_list:
                arg_option, arg_value = list_elm.split("=")
                arg_option = arg_option.lower()
                if arg_option == 'required' or arg_option == 'store_missing':
                    if arg_value.lower() == 'true':
                        arg_dict[arg_option] = True
                    else:
                        arg_dict[arg_option] = False
                elif arg_option == 'choices':
                    arg_value_list = arg_value.split(',')
                    arg_dict[arg_option] = arg_value_list
                else:
                    arg_dict[arg_option] = arg_value

        if help_message_text is not None:
            arg_dict['help'] = help_message_text
        return arg_dict

    @staticmethod
    def create_api_parser():
        """
        Creates an instance of RequestParser. This allows the use of the RequestParser.add_argument() method to be used
        to add what arguments are looked for. User handles call to the add_argument() method.

        :return: instance of RequestParser()
        """

        return reqparse.RequestParser()

    @staticmethod
    def add_common_request_args(parser_instance):
        """
        Adds common parameters needed by the USCC Engineering API.

        :param parser_instance: Instance of RequestParser
        :return: Nothing
        """

        list_o_db = ['hbase']
        db_name_help_message = "Parameter 'db_name' either missing or incorrect value given. Choices are %s." % list_o_db
        parser_instance.add_argument('db_name', required=True, choices=list_o_db, help=db_name_help_message)

        return

    @staticmethod
    def parse_request_args(parser_instance, strict_parm_list=True):
        """
        Calls the RequestParser instances parse_args method with the 'strict=True' parameter which will throw a 400
        Bad Request exception if the HTTP request contains arguments not defined.

        :param parser_instance: instance of RequestParser
        :param strict_parm_list: Indicates whether call to request parser should have strict flag set to True/False
        :return: parsed arguments as documented by RequestParser.parse_args() class instance method.
        """

        args = parser_instance.parse_args(strict=strict_parm_list)
        return args

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
            except Exception:
                traceback.print_exc()
                return False, None
        else:
            return False, "Value for parameter 'mode' invalid. Expected 'read' or 'write'"
