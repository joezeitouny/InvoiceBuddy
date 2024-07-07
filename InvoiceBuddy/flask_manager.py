import time
import webbrowser
from flask import render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from rich.console import Console
import json

from InvoiceBuddy import app
from InvoiceBuddy import globals, utils
from InvoiceBuddy.log_manager import LogManager

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{globals.DATABASE_NAME}.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(50), unique=True, nullable=False)
    invoice_date = db.Column(db.Date, nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    customer_name = db.Column(db.String(100), nullable=False)
    reference_number = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    items = db.Column(db.Text, nullable=False)  # Store items as JSON
    total_amount = db.Column(db.Float, nullable=False)
    seller_logo_path = db.Column(db.String(255), nullable=False)
    seller_name = db.Column(db.String(100), nullable=False)
    seller_address = db.Column(db.String(100), nullable=False)
    seller_country = db.Column(db.String(100), nullable=False)
    seller_phone = db.Column(db.String(100), nullable=False)
    seller_email = db.Column(db.String(100), nullable=False)
    seller_iban = db.Column(db.String(100), nullable=False)
    seller_bic = db.Column(db.String(100), nullable=False)
    seller_paypal_address = db.Column(db.String(100), nullable=False)
    currency_symbol = db.Column(db.String(100), nullable=False)
    currency_name = db.Column(db.String(100), nullable=False)
    invoice_terms_and_conditions = db.Column(db.Text, nullable=False)
    paid = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return dict(
            id=self.id,
            invoice_number=self.invoice_number,
            invoice_date=self.invoice_date.strftime('%Y/%m/%d'),
            due_date=self.due_date.strftime('%Y/%m/%d'),
            customer_name=self.customer_name,
            reference_number=self.reference_number,
            description=self.description,
            items=json.loads(self.items),
            total_amount=self.total_amount,
            seller_logo_path=self.seller_logo_path,
            seller_name=self.seller_name,
            seller_address=self.seller_address,
            seller_country=self.seller_country,
            seller_phone=self.seller_phone,
            seller_email=self.seller_email,
            seller_iban=self.seller_iban,
            seller_bic=self.seller_bic,
            seller_paypal_address=self.seller_paypal_address,
            currency_symbol=self.currency_symbol,
            currency_name=self.currency_name,
            invoice_terms_and_conditions=self.invoice_terms_and_conditions,
            paid=self.paid
        )


class Proposal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    proposal_number = db.Column(db.String(50), unique=True, nullable=False)
    proposal_date = db.Column(db.Date, nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    customer_name = db.Column(db.String(100), nullable=False)
    reference_number = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    items = db.Column(db.Text, nullable=False)  # Store items as JSON
    total_amount = db.Column(db.Float, nullable=False)
    seller_logo_path = db.Column(db.String(255), nullable=False)
    seller_name = db.Column(db.String(100), nullable=False)
    seller_address = db.Column(db.String(100), nullable=False)
    seller_country = db.Column(db.String(100), nullable=False)
    seller_phone = db.Column(db.String(100), nullable=False)
    seller_email = db.Column(db.String(100), nullable=False)
    seller_iban = db.Column(db.String(100), nullable=False)
    seller_bic = db.Column(db.String(100), nullable=False)
    seller_paypal_address = db.Column(db.String(100), nullable=False)
    currency_symbol = db.Column(db.String(100), nullable=False)
    currency_name = db.Column(db.String(100), nullable=False)
    proposal_terms_and_conditions = db.Column(db.Text, nullable=False)
    accepted = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return dict(
            id=self.id,
            proposal_number=self.proposal_number,
            proposal_date=self.proposal_date.strftime('%Y/%m/%d'),
            due_date=self.due_date.strftime('%Y/%m/%d'),
            customer_name=self.customer_name,
            reference_number=self.reference_number,
            description=self.description,
            items=json.loads(self.items),
            total_amount=self.total_amount,
            seller_logo_path=self.seller_logo_path,
            seller_name=self.seller_name,
            seller_address=self.seller_address,
            seller_country=self.seller_country,
            seller_phone=self.seller_phone,
            seller_email=self.seller_email,
            seller_iban=self.seller_iban,
            seller_bic=self.seller_bic,
            seller_paypal_address=self.seller_paypal_address,
            currency_symbol=self.currency_symbol,
            currency_name=self.currency_name,
            proposal_terms_and_conditions=self.proposal_terms_and_conditions,
            accepted=self.accepted
        )


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

        # Create tables before running the app
        with app.app_context():
            db.create_all()

        if self._options.web_launch_browser_during_startup:
            webbrowser.open(f'http://localhost:{self._options.web_port}')

        app.run(debug=False, host='0.0.0.0', port=self._options.web_port)


@app.route('/')
def index():
    # Get application name and version
    application_name = utils.get_application_name()
    application_version = utils.get_application_version()
    invoice_valid_for_days = application_modules.get_options().invoice_valid_for_days
    proposal_valid_for_days = application_modules.get_options().proposal_valid_for_days
    currency_symbol = application_modules.get_options().currency_symbol
    currency_name = application_modules.get_options().currency_name

    return render_template('index.html', application_name=application_name,
                           application_version=application_version, invoice_valid_for_days=invoice_valid_for_days,
                           proposal_valid_for_days=proposal_valid_for_days, currency_symbol=currency_symbol,
                           currency_name=currency_name)


@app.route('/new_invoice_number')
def new_invoice_number():
    try:
        # Open the configuration JSON file
        with open(f'{application_modules.get_options().configuration_path}', 'r') as file:
            data = json.load(file)

        invoice_number = data['invoice']['invoice_number']
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

    return jsonify(get_formatted_number(application_modules.get_options().invoice_prefix, invoice_number))


@app.route('/new_proposal_number')
def new_proposal_number():
    try:
        # Open the configuration JSON file
        with open(f'{application_modules.get_options().configuration_path}', 'r') as file:
            data = json.load(file)

        proposal_number = data['proposal']['proposal_number']
    except FileNotFoundError:
        application_modules.get_log_manager().info(
            f"Error: The file '{application_modules.get_options().configuration_path}' was not found while trying to "
            f"retrieve a new proposal number.")
        return jsonify(0)
    except json.JSONDecodeError:
        application_modules.get_log_manager().info("Error: Failed to decode JSON from the file while trying to "
                                                   "retrieve a new proposal number.")
        return jsonify(0)
    except Exception as e:
        application_modules.get_log_manager().info(
            f'An unexpected error occurred while trying to retrieve a new proposal number. Details {e}')
        return jsonify(0)

    return jsonify(get_formatted_number(application_modules.get_options().proposal_prefix, proposal_number))


@app.route('/generate_invoice', methods=['POST'])
def generate_invoice():
    if request.method == 'POST':
        items = json.loads(request.form['items'])
        total_amount = sum(item['quantity'] * item['price'] for item in items)
        for item in items:
            item['price'] = "{:.2f}".format(item['price'])
            item['amount'] = "{:.2f}".format(item['amount'])

        invoice_data = {
            'invoice_number': request.form['invoice_number'],
            'invoice_date': datetime.strptime(request.form['invoice_date'], '%Y-%m-%d').date(),
            'due_date': datetime.strptime(request.form['due_date'], '%Y-%m-%d').date(),
            'customer_name': request.form['customer_name'],
            'reference_number': request.form['reference_number'],
            'description': request.form['description'],
            'items': items,
            'total_amount': total_amount,
            'seller_logo_path': application_modules.get_options().seller_logo_path,
            'seller_name': application_modules.get_options().seller_name,
            'seller_address': application_modules.get_options().seller_address,
            'seller_country': application_modules.get_options().seller_country,
            'seller_phone': application_modules.get_options().seller_phone,
            'seller_email': application_modules.get_options().seller_email,
            'seller_iban': application_modules.get_options().seller_iban,
            'seller_bic': application_modules.get_options().seller_bic,
            'seller_paypal_address': application_modules.get_options().seller_paypal_address,
            'currency_symbol': application_modules.get_options().currency_symbol,
            'currency_name': application_modules.get_options().currency_name,
            'invoice_terms_and_conditions': application_modules.get_options().invoice_terms_and_conditions
        }

        new_invoice = Invoice(
            invoice_number=invoice_data['invoice_number'],
            invoice_date=invoice_data['invoice_date'],
            due_date=invoice_data['due_date'],
            customer_name=invoice_data['customer_name'],
            reference_number=invoice_data['reference_number'],
            description=invoice_data['description'],
            items=json.dumps(items),
            total_amount=total_amount,
            seller_logo_path=invoice_data['seller_logo_path'],
            seller_name=invoice_data['seller_name'],
            seller_address=invoice_data['seller_address'],
            seller_country=invoice_data['seller_country'],
            seller_phone=invoice_data['seller_phone'],
            seller_email=invoice_data['seller_email'],
            seller_iban=invoice_data['seller_iban'],
            seller_bic=invoice_data['seller_bic'],
            seller_paypal_address=invoice_data['seller_paypal_address'],
            currency_symbol=invoice_data['currency_symbol'],
            currency_name=invoice_data['currency_name'],
            invoice_terms_and_conditions=invoice_data['invoice_terms_and_conditions'],
            paid=False
        )

        db.session.add(new_invoice)
        db.session.commit()

        try:
            # Open the configuration JSON file
            with open(f'{application_modules.get_options().configuration_path}', 'r') as file:
                data = json.load(file)

            invoice_number = data['invoice']['invoice_number']
            data['invoice']['invoice_number'] = utils.try_parse_int(invoice_number) + 1

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

        return jsonify(new_invoice.id)


@app.route('/generate_proposal', methods=['POST'])
def generate_proposal():
    if request.method == 'POST':
        items = json.loads(request.form['items'])
        total_amount = sum(item['quantity'] * item['price'] for item in items)
        for item in items:
            item['price'] = "{:.2f}".format(item['price'])
            item['amount'] = "{:.2f}".format(item['amount'])

        proposal_data = {
            'proposal_number': request.form['proposal_number'],
            'proposal_date': datetime.strptime(request.form['proposal_date'], '%Y-%m-%d').date(),
            'due_date': datetime.strptime(request.form['due_date'], '%Y-%m-%d').date(),
            'customer_name': request.form['customer_name'],
            'reference_number': request.form['reference_number'],
            'description': request.form['description'],
            'items': items,
            'total_amount': total_amount,
            'seller_logo_path': application_modules.get_options().seller_logo_path,
            'seller_name': application_modules.get_options().seller_name,
            'seller_address': application_modules.get_options().seller_address,
            'seller_country': application_modules.get_options().seller_country,
            'seller_phone': application_modules.get_options().seller_phone,
            'seller_email': application_modules.get_options().seller_email,
            'seller_iban': application_modules.get_options().seller_iban,
            'seller_bic': application_modules.get_options().seller_bic,
            'seller_paypal_address': application_modules.get_options().seller_paypal_address,
            'currency_symbol': application_modules.get_options().currency_symbol,
            'currency_name': application_modules.get_options().currency_name,
            'proposal_terms_and_conditions': application_modules.get_options().proposal_terms_and_conditions
        }

        new_proposal = Proposal(
            proposal_number=proposal_data['proposal_number'],
            proposal_date=proposal_data['proposal_date'],
            due_date=proposal_data['due_date'],
            customer_name=proposal_data['customer_name'],
            reference_number=proposal_data['reference_number'],
            description=proposal_data['description'],
            items=json.dumps(items),
            total_amount=total_amount,
            seller_logo_path=proposal_data['seller_logo_path'],
            seller_name=proposal_data['seller_name'],
            seller_address=proposal_data['seller_address'],
            seller_country=proposal_data['seller_country'],
            seller_phone=proposal_data['seller_phone'],
            seller_email=proposal_data['seller_email'],
            seller_iban=proposal_data['seller_iban'],
            seller_bic=proposal_data['seller_bic'],
            seller_paypal_address=proposal_data['seller_paypal_address'],
            currency_symbol=proposal_data['currency_symbol'],
            currency_name=proposal_data['currency_name'],
            proposal_terms_and_conditions=proposal_data['proposal_terms_and_conditions'],
            accepted=False
        )

        db.session.add(new_proposal)
        db.session.commit()

        try:
            # Open the configuration JSON file
            with open(f'{application_modules.get_options().configuration_path}', 'r') as file:
                data = json.load(file)

            proposal_number = data['proposal']['proposal_number']
            data['proposal']['proposal_number'] = utils.try_parse_int(proposal_number) + 1

            with open(f'{application_modules.get_options().configuration_path}', 'w') as file:
                json.dump(data, file, indent=4)
        except FileNotFoundError:
            application_modules.get_log_manager().info(
                f"Error: The file '{application_modules.get_options().configuration_path}' was not found "
                f"while trying to "
                f"save a new proposal number.")
        except json.JSONDecodeError:
            application_modules.get_log_manager().info("Error: Failed to decode JSON from the file while trying to "
                                                       "save a new proposal number.")
        except Exception as e:
            application_modules.get_log_manager().info(
                f'An unexpected error occurred while trying to save a new proposal number. Details {e}')

        return jsonify(new_proposal.id)


@app.route('/view_invoice', methods=['GET'])
def view_invoice():
    if request.method == 'GET':
        invoice_id = request.args.get('invoice_id')
        show_print_dialog = False
        if not request.args.get('show_print_dialog') is None:
            show_print_dialog = True
        invoice = Invoice.query.get_or_404(invoice_id)

        invoice_data = {
            'invoice_number': invoice.invoice_number,
            'invoice_date': invoice.invoice_date,
            'due_date': invoice.due_date,
            'customer_name': invoice.customer_name,
            'reference_number': invoice.reference_number,
            'description': invoice.description,
            'items': json.loads(invoice.items),
            'total_amount': "{:.2f}".format(invoice.total_amount),
            'seller_logo_path': invoice.seller_logo_path,
            'seller_name': invoice.seller_name,
            'seller_address': invoice.seller_address,
            'seller_country': invoice.seller_country,
            'seller_phone': invoice.seller_phone,
            'seller_email': invoice.seller_email,
            'seller_iban': invoice.seller_iban,
            'seller_bic': invoice.seller_bic,
            'seller_paypal_address': invoice.seller_paypal_address,
            'currency_symbol': invoice.currency_symbol,
            'currency_name': invoice.currency_name,
            'invoice_terms_and_conditions': invoice.invoice_terms_and_conditions,
            'show_print_dialog': show_print_dialog
        }

        return render_template('invoice_template.html', **invoice_data)


@app.route('/view_proposal', methods=['GET'])
def view_proposal():
    if request.method == 'GET':
        proposal_id = request.args.get('proposal_id')
        show_print_dialog = False
        if not request.args.get('show_print_dialog') is None:
            show_print_dialog = True
        proposal = Proposal.query.get_or_404(proposal_id)

        proposal_data = {
            'proposal_number': proposal.proposal_number,
            'proposal_date': proposal.proposal_date,
            'due_date': proposal.due_date,
            'customer_name': proposal.customer_name,
            'reference_number': proposal.reference_number,
            'description': proposal.description,
            'items': json.loads(proposal.items),
            'total_amount': "{:.2f}".format(proposal.total_amount),
            'seller_logo_path': proposal.seller_logo_path,
            'seller_name': proposal.seller_name,
            'seller_address': proposal.seller_address,
            'seller_country': proposal.seller_country,
            'seller_phone': proposal.seller_phone,
            'seller_email': proposal.seller_email,
            'seller_iban': proposal.seller_iban,
            'seller_bic': proposal.seller_bic,
            'seller_paypal_address': proposal.seller_paypal_address,
            'currency_symbol': proposal.currency_symbol,
            'currency_name': proposal.currency_name,
            'proposal_terms_and_conditions': proposal.proposal_terms_and_conditions,
            'show_print_dialog': show_print_dialog
        }

        return render_template('proposal_template.html', **proposal_data)


@app.route('/invoices')
def list_invoices():
    invoices = Invoice.query.all()
    json_invoices = [invoice.to_dict() for invoice in invoices]

    return jsonify(json_invoices)


@app.route('/active_invoices')
def list_active_invoices():
    invoices = Invoice.query.filter(Invoice.paid == False).all()
    json_invoices = [invoice.to_dict() for invoice in invoices]

    return jsonify(json_invoices)


@app.route('/past_invoices')
def list_past_invoices():
    invoices = Invoice.query.filter(Invoice.paid == True).all()
    json_invoices = [invoice.to_dict() for invoice in invoices]

    return jsonify(json_invoices)


@app.route('/past_invoices_count')
def past_invoices_count():
    invoices = Invoice.query.filter(Invoice.paid == True).all()

    return jsonify(len(invoices))


@app.route('/proposals')
def list_proposals():
    proposals = Proposal.query.all()
    json_proposals = [proposal.to_dict() for proposal in proposals]

    return jsonify(json_proposals)


@app.route('/active_proposals')
def list_active_proposals():
    proposals = Proposal.query.filter(Proposal.accepted == False).all()
    json_proposals = [proposal.to_dict() for proposal in proposals]

    return jsonify(json_proposals)


@app.route('/past_proposals')
def list_past_proposals():
    proposals = Proposal.query.filter(Proposal.accepted == True).all()
    json_proposals = [proposal.to_dict() for proposal in proposals]

    return jsonify(json_proposals)


@app.route('/past_proposals_count')
def past_proposals_count():
    proposals = Proposal.query.filter(Proposal.accepted == True).all()

    return jsonify(len(proposals))


@app.route('/mark_invoice_paid', methods=['POST'])
def mark_invoice_paid():
    if request.method == 'POST':
        try:
            invoice_number = request.form['invoice_number']
            invoice = Invoice.query.filter(Invoice.invoice_number == invoice_number).first()
            invoice.paid = True
            db.session.commit()

            return jsonify(True)
        except Exception as e:
            application_modules.get_log_manager().warning(
                f"Exception occurred while trying to mark invoice as paid. Details: {e}")
            return jsonify(False)

    return jsonify(False)


@app.route('/mark_proposal_accepted', methods=['POST'])
def mark_proposal_accepted():
    if request.method == 'POST':
        try:
            proposal_number = request.form['proposal_number']
            proposal = Invoice.query.filter(Proposal.proposal_number == proposal_number).first()
            proposal.accepted = True
            db.session.commit()

            return jsonify(True)
        except Exception as e:
            application_modules.get_log_manager().warning(
                f"Exception occurred while trying to mark invoice as paid. Details: {e}")
            return jsonify(False)

    return jsonify(False)


def get_formatted_number(prefix, sequence_number):
    # Get the current year
    current_year = datetime.now().year

    # Format the sequence number with zero padding (6 digits)
    sequence_str = f'{sequence_number:05d}'

    # Concatenate year and sequence number
    formatted_number = f'{prefix}{current_year}{sequence_str}'

    return formatted_number
