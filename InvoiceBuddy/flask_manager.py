import time
import webbrowser
from flask import render_template, request, make_response, send_file, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
import pdfkit
from datetime import datetime
from rich.console import Console
import os
import json

from InvoiceBuddy import app
from InvoiceBuddy import globals, utils
from InvoiceBuddy.log_manager import LogManager

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{globals.DATABASE_NAME}.db'
app.config['INVOICE_FOLDER'] = globals.INVOICE_FOLDER
app.config['PROPOSALS_FOLDER'] = globals.PROPOSAL_FOLDER
db = SQLAlchemy(app)


class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(50), unique=True, nullable=False)
    invoice_date = db.Column(db.Date, nullable=False)
    customer_name = db.Column(db.String(100), nullable=False)
    reference_number = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    items = db.Column(db.Text, nullable=False)  # Store items as JSON
    total_amount = db.Column(db.Float, nullable=False)
    pdf_path = db.Column(db.String(255), nullable=False)
    paid = db.Column(db.Boolean, default=False)


class Proposal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    proposal_number = db.Column(db.String(50), unique=True, nullable=False)
    proposal_date = db.Column(db.Date, nullable=False)
    customer_name = db.Column(db.String(100), nullable=False)
    reference_number = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    items = db.Column(db.Text, nullable=False)  # Store items as JSON
    total_amount = db.Column(db.Float, nullable=False)
    pdf_path = db.Column(db.String(255), nullable=False)
    accepted = db.Column(db.Boolean, default=False)


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


@app.route('/new_invoice_number')
def new_invoice_number():
    try:
        # Open the configuration JSON file
        with open(f'{application_modules.get_options().configuration_path}', 'r') as file:
            data = json.load(file)

        invoice_number = data['invoice_number']
    except FileNotFoundError:
        application_modules.get_log_manager().info(
            f"Error: The file '{application_modules.get_options().configuration_path}' was not found while trying to "
            f"retrieve a new invoice number.")
        return jsonify(0)
    except json.JSONDecodeError:
        application_modules.get_log_manager().info("Error: Failed to decode JSON from the file while trying to "
                                                   "retrieve a new invoice number.")
        return jsonify(0)
    except Exception as e:
        application_modules.get_log_manager().info(
            f'An unexpected error occurred while trying to retrieve a new invoice number. Details {e}')
        return jsonify(0)

    return jsonify(get_formatted_number(invoice_number))


@app.route('/generate_invoice', methods=['POST'])
def generate_invoice():
    if request.method == 'POST':
        items = json.loads(request.form['items'])
        total_amount = sum(item['quantity'] * item['price'] for item in items)

        invoice_data = {
            'invoice_number': request.form['invoice_number'],
            'invoice_date': datetime.strptime(request.form['invoice_date'], '%Y-%m-%d').date(),
            'customer_name': request.form['customer_name'],
            'reference_number': request.form['reference_number'],
            'description': request.form['description'],
            'items': items,
            'total_amount': total_amount
        }

        html = render_template('invoice_template.html', **invoice_data)
        pdf = pdfkit.from_string(html, False)

        if not os.path.exists(app.config['INVOICE_FOLDER']):
            os.makedirs(app.config['INVOICE_FOLDER'])
        pdf_path = os.path.join(app.config['INVOICE_FOLDER'], f"invoice_{invoice_data['invoice_number']}.pdf")
        with open(pdf_path, 'wb') as pdf_file:
            pdf_file.write(pdf)

        new_invoice = Invoice(
            invoice_number=invoice_data['invoice_number'],
            invoice_date=invoice_data['invoice_date'],
            customer_name=invoice_data['customer_name'],
            reference_number=invoice_data['reference_number'],
            description=invoice_data['description'],
            items=json.dumps(items),
            total_amount=total_amount,
            pdf_path=pdf_path,
            paid=False
        )
        db.session.add(new_invoice)
        db.session.commit()

        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=invoice_{invoice_data["invoice_number"]}.pdf'

        try:
            # Open the configuration JSON file
            with open(f'{application_modules.get_options().configuration_path}', 'r') as file:
                data = json.load(file)

            invoice_number = data['invoice_number']
            data['invoice_number'] = utils.try_parse_int(invoice_number) + 1

            with open(f'{application_modules.get_options().configuration_path}', 'w') as file:
                json.dump(data, file, indent=4)
        except FileNotFoundError:
            application_modules.get_log_manager().info(
                f"Error: The file '{application_modules.get_options().configuration_path}' was not found "
                f"while trying to "
                f"save a new invoice number.")
        except json.JSONDecodeError:
            application_modules.get_log_manager().info("Error: Failed to decode JSON from the file while trying to "
                                                       "save a new invoice number.")
        except Exception as e:
            application_modules.get_log_manager().info(
                f'An unexpected error occurred while trying to save a new invoice number. Details {e}')

        return response


@app.route('/invoices')
def list_invoices():
    invoices = Invoice.query.all()
    return render_template('invoice_list.html', invoices=invoices)


@app.route('/proposals')
def list_proposals():
    proposals = Proposal.query.all()
    return render_template('proposal_list.html', proposals=proposals)


@app.route('/download/<int:invoice_id>')
def download_invoice(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)
    return send_file(invoice.pdf_path, as_attachment=True)


@app.route('/toggle_paid/<int:invoice_id>')
def toggle_paid(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)
    invoice.paid = not invoice.paid
    db.session.commit()
    return redirect(url_for('list_invoices'))


@app.route('/toggle_accepted/<int:proposal_id>')
def toggle_accepted(proposal_id):
    proposal = Proposal.query.get_or_404(proposal_id)
    proposal.accepted = not proposal.accepted
    db.session.commit()
    return redirect(url_for('list_proposals'))


def get_formatted_number(sequence_number):
    # Get the current year
    current_year = datetime.now().year

    # Format the sequence number with zero padding (6 digits)
    sequence_str = f'{sequence_number:05d}'

    # Concatenate year and sequence number
    formatted_number = f'{current_year}{sequence_str}'

    return formatted_number
