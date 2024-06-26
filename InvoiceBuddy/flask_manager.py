import math
import time
import webbrowser
from threading import Thread, Event, Lock

from flask import render_template, jsonify, request
from rich.console import Console

from InvoiceBuddy import app
from InvoiceBuddy import globals, utils
from InvoiceBuddy.email_manager import EmailManager
from InvoiceBuddy.log_manager import LogManager


class ApplicationModules:
    def __init__(self, options, log_manager: LogManager, email_manager: EmailManager):
        self._options = options
        self._log_manager = log_manager
        self._email_manager = email_manager

    def get_options(self):
        return self._options

    def get_log_manager(self) -> LogManager:
        return self._log_manager

    def get_email_manager(self) -> EmailManager:
        return self._email_manager


application_modules: ApplicationModules
cached_data: {}
flask_manager_thread: None
exit_signal: Event()
mutex: Lock()


class FlaskManager:
    def __init__(self, options):
        self._options = options

        # Create a console instance
        _console = Console()
        _console.print(f'[bright_yellow]Application is starting up. Please wait...[/bright_yellow]')

        with _console.status('[bold bright_yellow]Loading logging module...[/bold bright_yellow]'):
            time.sleep(0.1)
            _log_manager = LogManager(self._options)
            _console.print(f'[green]Loading logging module...Done[/green]')

        with _console.status('[bold bright_yellow]Loading email module...[/bold bright_yellow]'):
            time.sleep(0.1)
            _email_manager = EmailManager(self._options, _log_manager)
            _console.print(f'[green]Loading email module...Done[/green]')

        global application_modules
        application_modules = ApplicationModules(self._options, _log_manager, _email_manager)

        if self._options.web_launch_browser_during_startup:
            webbrowser.open(f'http://localhost:{self._options.web_port}')

        app.run(debug=False, host='0.0.0.0', port=self._options.web_port)


@app.route('/')
def index():
    # Get application name and version
    application_name = utils.get_application_name()
    application_version = utils.get_application_version()

    return render_template('index.html', application_name=application_name, application_version=application_version)



