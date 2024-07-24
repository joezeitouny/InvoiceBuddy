import json
import logging
import optparse
import os

from InvoiceBuddy import globals, utils, app

CONFIG_FILE_PATH = os.environ.get('CONFIG_ FILE_ PATH', '/InvoiceBuddy/sample-config.json')


def parse_config(options):
    try:
        with open(options.configuration_path) as f:
            data = json.load(f)

            options.output_path = data['output_path']
            options.tmp_path = data['tmp_path']
            options.filename_prefix = data['filename_prefix']
            options.currency_symbol = data['currency_symbol']
            options.currency_name = data['currency_name']
            options.web_launch_browser_during_startup = utils.try_parse_bool(
                data['web_application']['web_launch_browser_during_startup'])
            options.web_port = data['web_application']['web_port']
            options.log_module = utils.try_parse_bool(data['log']['log_module'])
            options.log_level = data['log']['log_level']
            options.invoice_prefix = data['invoice']['invoice_prefix']
            options.invoice_number = utils.try_parse_int(data['invoice']['invoice_number'])
            options.invoice_valid_for_days = utils.try_parse_int(data['invoice']['invoice_valid_for_days'])
            options.invoice_terms_and_conditions = data['invoice']['invoice_terms_and_conditions']
            options.proposal_prefix = data['proposal']['proposal_prefix']
            options.proposal_number = utils.try_parse_int(data['proposal']['proposal_number'])
            options.proposal_valid_for_days = utils.try_parse_int(data['proposal']['proposal_valid_for_days'])
            options.proposal_terms_and_conditions = data['proposal']['proposal_terms_and_conditions']
            options.seller_name = data['seller']['seller_name']
            options.seller_address = data['seller']['seller_address']
            options.seller_country = data['seller']['seller_country']
            options.seller_phone = data['seller']['seller_phone']
            options.seller_email = data['seller']['seller_email']
            options.seller_iban = data['seller']['seller_iban']
            options.seller_bic = data['seller']['seller_bic']
            options.seller_paypal_address = data['seller']['seller_paypal_address']
    except Exception as e:
        print(f'Error while parsing the specified JSON configuration file. Details {e}\r\n')
        quit()

    return options


def main():
    # Create an options list using the Options Parser
    parser = optparse.OptionParser()
    parser.set_description(f'Version {globals.APPLICATION_VERSION}. '
                           f'A tool to help with generating invoices and proposals for freelancers '
                           f'or small businesses.')
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
        options = parse_config(options)

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
            resulting_path = os.path.join(options.tmp_path, f"{globals.DATABASE_NAME}.db")
            app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{resulting_path}'
            app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
            from InvoiceBuddy.flask_manager import FlaskManager
            FlaskManager(options)


if __name__ == '__main__':
    main()
