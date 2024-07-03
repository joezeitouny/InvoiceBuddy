import json
import logging
import optparse
import os

from InvoiceBuddy import globals, utils
from InvoiceBuddy.flask_manager import FlaskManager

if __name__ == '__main__':
    # Create an options list using the Options Parser
    parser = optparse.OptionParser()
    parser.set_description(f'Version {globals.APPLICATION_VERSION}. '
                           f'Helps with generating invoices and proposals for freelancers.')
    parser.set_usage(f'python3 -m {globals.APPLICATION_NAME} --config=CONFIGURATION_PATH')
    parser.add_option('--config', dest='configuration_path', type='string', help=f'Path to the configuration file')

    (options, args) = parser.parse_args()

    # Check if the CONFIG_PATH environment variable is set
    default_configuration_path = '/InvoiceBuddy/sample-config.json'
    env_configuration_path = os.environ.get('CONFIG_FILE_PATH', default_configuration_path)
    if env_configuration_path != default_configuration_path and not options.configuration_path:
        options.configuration_path = env_configuration_path

    if not options.configuration_path:
        print(f'Invalid argument: Configuration path is a required argument\r\n')
        parser.print_help()
    elif not os.path.exists(options.configuration_path):
        print(f'Invalid argument: Valid JSON configuration file path is required\r\n')
        parser.print_help()
    else:
        try:
            # Open the configuration JSON file
            f = open(f'{options.configuration_path}')

            # returns JSON object as
            # a dictionary
            data = json.load(f)

            options.output_path = data['output_path']
            options.tmp_path = data['tmp_path']
            options.filename_prefix = data['filename_prefix']
            options.web_launch_browser_during_startup = utils.try_parse_bool(
                data['web_application']['web_launch_browser_during_startup'])
            options.web_port = data['web_application']['web_port']
            options.log_module = utils.try_parse_bool(data['log']['log_module'])
            options.log_level = data['log']['log_level']
        except Exception as e:
            print(f'Error while parsing the specified JSON configuration file. Details {e}\r\n')
            parser.print_help()
            quit()

        log_numeric_level = getattr(logging, options.log_level.upper(), None)
        if not options.output_path:
            print(f'Invalid argument: Output directory defined in OUTPUT_PATH is required.\r\n')
            parser.print_help()
        elif not isinstance(log_numeric_level, int):
            print(f'Invalid argument: Log level "{options.log_level}"')
            parser.print_help()
        elif not options.web_port:
            print(f'Invalid argument: Web module requires port parameter to be provided')
        else:
            FlaskManager(options)