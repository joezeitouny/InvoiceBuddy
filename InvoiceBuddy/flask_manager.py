import time
import webbrowser

from flask import Flask, render_template, jsonify, request, send_file
from weasyprint import HTML
import io
from rich.console import Console

from InvoiceBuddy import app
from InvoiceBuddy import globals, utils
from InvoiceBuddy.log_manager import LogManager


class ApplicationModules:
    def __init__(self, options, log_manager: LogManager):
        self._options = options
        self._log_manager = log_manager

    def get_options(self):
        return self._options

    def get_log_manager(self) -> LogManager:
        return self._log_manager


application_modules: ApplicationModules


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

        global application_modules
        application_modules = ApplicationModules(self._options, _log_manager)

        if self._options.web_launch_browser_during_startup:
            webbrowser.open(f'http://localhost:{self._options.web_port}')

        app.run(debug=False, host='0.0.0.0', port=self._options.web_port)


@app.route('/')
def index():
    # Get application name and version
    application_name = utils.get_application_name()
    application_version = utils.get_application_version()

    return render_template('index.html', application_name=application_name, application_version=application_version)


@app.route('/generate_invoice', methods=['GET', 'POST'])
def generate_invoice():
    if request.method == 'POST':
        # Get form data
        invoice_data = {
            'invoice_number': request.form['invoice_number'],
            'date': request.form['date'],
            'client_name': request.form['client_name'],
            'items': []
        }

        # Process items
        descriptions = request.form.getlist('item_description[]')
        quantities = request.form.getlist('item_quantity[]')
        prices = request.form.getlist('item_price[]')

        for desc, qty, price in zip(descriptions, quantities, prices):
            item = {
                'description': desc,
                'quantity': int(qty),
                'price': float(price),
                'total': int(qty) * float(price)
            }
            invoice_data['items'].append(item)

        # Calculate total amount
        invoice_data['total_amount'] = sum(item['total'] for item in invoice_data['items'])

        # Render the HTML template
        html_content = render_template('invoice_template.html', **invoice_data)

        # Generate PDF
        pdf = HTML(string=html_content).write_pdf()

        # Create a response with the PDF file
        pdf_buffer = io.BytesIO(pdf)
        pdf_buffer.seek(0)

        return send_file(
            pdf_buffer,
            download_name='invoice.pdf',
            as_attachment=True,
            mimetype='application/pdf'
        )

    return render_template('invoice_form.html')


