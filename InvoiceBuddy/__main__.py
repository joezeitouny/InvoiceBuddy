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
    default_configuration_path = '/TradingBot/sample-config.json'
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
            options.run_in_simulation_mode = utils.try_parse_bool(data['run_in_simulation_mode'])
            options.exchange_name = data['exchange']['exchange_name']
            options.exchange_api_keys = data['exchange']['exchange_api_keys']
            options.exchange_api_secret = data['exchange']['exchange_api_secret']
            options.exchange_test_net = data['exchange']['exchange_test_net']
            options.web_module = utils.try_parse_bool(data['web_application']['web_module'])
            options.web_host = data['web_application']['web_host']
            options.web_port = data['web_application']['web_port']
            options.web_environment = data['web_application']['web_environment']
            options.email_module = utils.try_parse_bool(data['email']['email_module'])
            options.email_address = data['email']['email_address']
            options.email_password = data['email']['email_password']
            options.email_trade_report = utils.try_parse_bool(data['email']['email_trade_report'])
            options.notifications_module = utils.try_parse_bool(data['notification']['notifications_module'])
            options.notification_email = utils.try_parse_bool(data['notification']['notification_email'])
            options.notification_sound = utils.try_parse_bool(data['notification']['notification_sound'])
            options.notification_console = utils.try_parse_bool(data['notification']['notification_console'])
            options.notification_cool_off_interval = utils.try_parse_int(
                data['notification']['notification_cool_off_interval'])
            options.log_module = utils.try_parse_bool(data['log']['log_module'])
            options.log_level = data['log']['log_level']
            options.sound_module = utils.try_parse_bool(data['sound']['sound_module'])
            options.trades_rules = data['trades_rules']
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
        elif not options.exchange_name or options.exchange_name != 'bybit':
            print(f'Exchange name needs to be provided. Only ByBit exchange is supported at the moment!')
            parser.print_help()
        elif not options.exchange_api_keys or not options.exchange_api_secret:
            print(f'Both API keys and secret for the exchange need to be provided')
            parser.print_help()
        elif options.email_module and not (options.email_address or options.email_password):
            print(f'Invalid argument: Email credentials need to be supplied in order to use the email module')
        elif options.notifications_module and not options.notification_cool_off_interval:
            print(f'Invalid argument: Notification cool-off interval need to be provided if the '
                  f'notification module is turned on')
        elif options.web_module and not (options.web_host or options.web_port or options.web_environment):
            print(f'Invalid argument: Web module requires the host and port and environment parameters to be provided')
        else:
            # Set the environment variable FLASK_ENV
            os.environ['FLASK_ENV'] = options.web_environment
            FlaskManager(options)
