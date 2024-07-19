import math
import time
import webbrowser
from flask import render_template, request, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from rich.console import Console
import json
import os
import qrcode

from InvoiceBuddy import app
from InvoiceBuddy import globals, utils
from InvoiceBuddy.log_manager import LogManager

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
    status = db.Column(db.Integer, nullable=False, default=0)

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
            status=self.status
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
    status = db.Column(db.Integer, nullable=False, default=0)

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
            status=self.status
        )


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)

    def to_dict(self):
        return dict(
            id=self.id,
            title=self.title,
            description=self.description,
            price=self.price
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


@app.route('/upload_config', methods=['POST'])
def upload_config():
    if 'config_file' in request.files:
        file = request.files['config_file']
        if file and is_json_file(file.filename):
            try:
                file.save(application_modules.get_options().configuration_path)
                # Store the uploaded JSON file on your server
                return 'System configuration updated successfully!'
            except Exception as e:
                return f'Error while trying to update the configuration on the server. Details: {e}'
    return 'Invalid file type'


@app.route('/upload_seller_logo', methods=['POST'])
def upload_seller_logo():
    if 'seller_logo' in request.files:
        file = request.files['seller_logo']

        # Get the path of the static directory
        static_folder_path = app.static_folder

        # Get the absolute path
        absolute_static_path = os.path.abspath(static_folder_path)
        resulting_path = os.path.join(absolute_static_path, "seller-logo.png")

        if file:
            try:
                file.save(resulting_path)
                # Store the uploaded JSON file on your server
                return 'Seller logo successfully updated!'
            except Exception as e:
                return f'Error while trying to update the seller logo on the server. Details: {e}'

    return 'Invalid file type'


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


@app.route('/add_item', methods=['POST'])
def add_item():
    if request.method == 'POST':
        item_data = {
            'title': request.form['title'],
            'description': request.form['description'],
            'price': request.form['price']
        }

        new_item = Item(
            title=item_data['title'],
            description=item_data['description'],
            price=item_data['price']
        )

        db.session.add(new_item)
        db.session.commit()

        return jsonify(new_item.id)


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
            'invoice_terms_and_conditions': application_modules.get_options().invoice_terms_and_conditions,
            'status': 0
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
            status=invoice_data['status']
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
            'proposal_terms_and_conditions': application_modules.get_options().proposal_terms_and_conditions,
            'status': 0
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
            status=proposal_data['status']
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

        img = qrcode.make(invoice.seller_iban)
        # Get the path of the static directory
        static_folder_path = app.static_folder

        # Get the absolute path
        absolute_static_path = os.path.abspath(static_folder_path)
        img.save(os.path.join(absolute_static_path, "seller-qr-code.png"))

        invoice_data = {
            'invoice_number': invoice.invoice_number,
            'invoice_date': invoice.invoice_date,
            'due_date': invoice.due_date,
            'customer_name': invoice.customer_name,
            'reference_number': invoice.reference_number,
            'description': invoice.description,
            'items': json.loads(invoice.items),
            'total_amount': "{:.2f}".format(invoice.total_amount),
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
            'status': invoice.status,
            'show_print_dialog': show_print_dialog
        }

        for item in invoice_data['items']:
            item['description'] = item['description'].replace('\n', '<br>')

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
            'status': proposal.status,
            'show_print_dialog': show_print_dialog
        }

        for item in proposal_data['items']:
            item['description'] = item['description'].replace('\n', '<br>')

        return render_template('proposal_template.html', **proposal_data)


@app.route('/invoices')
def list_invoices():
    invoices = Invoice.query.all()
    json_invoices = [invoice.to_dict() for invoice in invoices]

    return jsonify(json_invoices)


@app.route('/active_invoices')
def list_active_invoices():
    invoices = Invoice.query.filter(Invoice.status == 0).all()
    json_invoices = [invoice.to_dict() for invoice in invoices]

    return jsonify(json_invoices)


@app.route('/view_past_invoices')
def view_past_invoices():
    # Get application name and version
    application_name = utils.get_application_name()
    application_version = utils.get_application_version()
    invoice_valid_for_days = application_modules.get_options().invoice_valid_for_days
    proposal_valid_for_days = application_modules.get_options().proposal_valid_for_days
    currency_symbol = application_modules.get_options().currency_symbol
    currency_name = application_modules.get_options().currency_name

    return render_template('past_invoices.html', application_name=application_name,
                           application_version=application_version, invoice_valid_for_days=invoice_valid_for_days,
                           proposal_valid_for_days=proposal_valid_for_days, currency_symbol=currency_symbol,
                           currency_name=currency_name)


@app.route('/past_invoices')
def list_past_invoices():
    page = int(request.args.get('page', 1))
    items_per_page = globals.PAST_INVOICES_TABLE_ITEMS_PER_PAGE

    start_idx = (page - 1) * items_per_page
    end_idx = start_idx + items_per_page

    invoices = Invoice.query.filter(Invoice.status != 0).all()
    paginated_data = [invoice.to_dict() for invoice in invoices[start_idx:end_idx]]

    total_number_of_pages = math.floor(len(invoices) / items_per_page)
    if len(invoices) % items_per_page != 0:
        total_number_of_pages += 1

    total_number_of_invoices = len(invoices)

    data = {'past_invoices': paginated_data,
            'total_number_of_pages': total_number_of_pages,
            'total_number_of_invoices': total_number_of_invoices}

    return jsonify(data)


@app.route('/past_invoices_count')
def past_invoices_count():
    invoices = Invoice.query.filter(Invoice.status != 0).all()

    return jsonify(len(invoices))


@app.route('/proposals')
def list_proposals():
    proposals = Proposal.query.all()
    json_proposals = [proposal.to_dict() for proposal in proposals]

    return jsonify(json_proposals)


@app.route('/active_proposals')
def list_active_proposals():
    proposals = Proposal.query.filter(Proposal.status == 0).all()
    json_proposals = [proposal.to_dict() for proposal in proposals]

    return jsonify(json_proposals)


@app.route('/view_past_proposals')
def view_past_proposals():
    # Get application name and version
    application_name = utils.get_application_name()
    application_version = utils.get_application_version()
    invoice_valid_for_days = application_modules.get_options().invoice_valid_for_days
    proposal_valid_for_days = application_modules.get_options().proposal_valid_for_days
    currency_symbol = application_modules.get_options().currency_symbol
    currency_name = application_modules.get_options().currency_name

    return render_template('past_proposals.html', application_name=application_name,
                           application_version=application_version, invoice_valid_for_days=invoice_valid_for_days,
                           proposal_valid_for_days=proposal_valid_for_days, currency_symbol=currency_symbol,
                           currency_name=currency_name)


@app.route('/past_proposals')
def list_past_proposals():
    page = int(request.args.get('page', 1))
    items_per_page = globals.PAST_PROPOSALS_TABLE_ITEMS_PER_PAGE

    start_idx = (page - 1) * items_per_page
    end_idx = start_idx + items_per_page

    proposals = Proposal.query.filter(Proposal.status != 0).all()
    paginated_data = [proposal.to_dict() for proposal in proposals[start_idx:end_idx]]

    total_number_of_pages = math.floor(len(proposals) / items_per_page)
    if len(proposals) % items_per_page != 0:
        total_number_of_pages += 1

    total_number_of_proposals = len(proposals)

    data = {'past_proposals': paginated_data,
            'total_number_of_pages': total_number_of_pages,
            'total_number_of_proposals': total_number_of_proposals}

    return jsonify(data)


@app.route('/past_proposals_count')
def past_proposals_count():
    proposals = Proposal.query.filter(Proposal.status != 0).all()

    return jsonify(len(proposals))


@app.route('/delete_item', methods=['POST'])
def delete_item():
    if request.method == 'POST':
        try:
            item_id = request.form['item_id']

            item_to_delete = db.session.query(Item).filter_by(id=item_id).one()
            db.session.delete(item_to_delete)
            db.session.commit()

            return jsonify(True)
        except Exception as e:
            application_modules.get_log_manager().warning(
                f"Exception occurred while trying to delete item. Details: {e}")
            return jsonify(False)

    return jsonify(False)


@app.route('/mark_invoice_canceled', methods=['POST'])
def mark_invoice_canceled():
    if request.method == 'POST':
        try:
            invoice_number = request.form['invoice_number']
            invoice = Invoice.query.filter(Invoice.invoice_number == invoice_number).first()
            invoice.status = 2

            db.session.commit()

            return jsonify(True)
        except Exception as e:
            application_modules.get_log_manager().warning(
                f"Exception occurred while trying to mark invoice as canceled. Details: {e}")
            return jsonify(False)

    return jsonify(False)


@app.route('/mark_invoice_paid', methods=['POST'])
def mark_invoice_paid():
    if request.method == 'POST':
        try:
            invoice_number = request.form['invoice_number']
            invoice = Invoice.query.filter(Invoice.invoice_number == invoice_number).first()
            invoice.status = 1
            db.session.commit()

            return jsonify(True)
        except Exception as e:
            application_modules.get_log_manager().warning(
                f"Exception occurred while trying to mark invoice as paid. Details: {e}")
            return jsonify(False)

    return jsonify(False)


@app.route('/mark_proposal_rejected', methods=['POST'])
def mark_proposal_rejected():
    if request.method == 'POST':
        try:
            proposal_number = request.form['proposal_number']
            proposal = Proposal.query.filter(Proposal.proposal_number == proposal_number).first()
            proposal.status = 2

            db.session.commit()

            return jsonify(True)
        except Exception as e:
            application_modules.get_log_manager().warning(
                f"Exception occurred while trying to mark proposal as rejected. Details: {e}")
            return jsonify(False)

    return jsonify(False)


@app.route('/mark_proposal_accepted', methods=['POST'])
def mark_proposal_accepted():
    if request.method == 'POST':
        try:
            proposal_number = request.form['proposal_number']
            proposal = Proposal.query.filter(Proposal.proposal_number == proposal_number).first()
            proposal.status = 1

            # create a new invoice from the accepted proposal
            invoice_number = new_invoice_number()
            new_invoice = Invoice(
                invoice_number=invoice_number.json,
                invoice_date=datetime.now(),
                due_date=datetime.now() + timedelta(days=application_modules.get_options().invoice_valid_for_days),
                customer_name=proposal.customer_name,
                reference_number=proposal.reference_number,
                description=proposal.description,
                items=proposal.items,
                total_amount=proposal.total_amount,
                seller_name=proposal.seller_name,
                seller_address=proposal.seller_address,
                seller_country=proposal.seller_country,
                seller_phone=proposal.seller_phone,
                seller_email=proposal.seller_email,
                seller_iban=proposal.seller_iban,
                seller_bic=proposal.seller_bic,
                seller_paypal_address=proposal.seller_paypal_address,
                currency_symbol=proposal.currency_symbol,
                currency_name=proposal.currency_name,
                invoice_terms_and_conditions=application_modules.get_options().invoice_terms_and_conditions,
                status=0
            )
            db.session.add(new_invoice)
            db.session.commit()

            return jsonify(True)
        except Exception as e:
            application_modules.get_log_manager().warning(
                f"Exception occurred while trying to mark proposal as accepted. Details: {e}")
            return jsonify(False)

    return jsonify(False)


@app.route('/view_items')
def view_items():
    # Get application name and version
    application_name = utils.get_application_name()
    application_version = utils.get_application_version()
    invoice_valid_for_days = application_modules.get_options().invoice_valid_for_days
    proposal_valid_for_days = application_modules.get_options().proposal_valid_for_days
    currency_symbol = application_modules.get_options().currency_symbol
    currency_name = application_modules.get_options().currency_name

    return render_template('items.html', application_name=application_name,
                           application_version=application_version, invoice_valid_for_days=invoice_valid_for_days,
                           proposal_valid_for_days=proposal_valid_for_days, currency_symbol=currency_symbol,
                           currency_name=currency_name)


@app.route('/items')
def list_items():
    page = int(request.args.get('page', 1))
    items_per_page = globals.ITEMS_ITEMS_PER_PAGE

    start_idx = (page - 1) * items_per_page
    end_idx = start_idx + items_per_page

    items = Item.query.all()
    paginated_data = [item.to_dict() for item in items[start_idx:end_idx]]

    for item in paginated_data:
        item['description'] = item['description'].replace('\n', '<br>')

    total_number_of_pages = math.floor(len(items) / items_per_page)
    if len(items) % items_per_page != 0:
        total_number_of_pages += 1

    total_number_of_invoices = len(items)

    data = {'items': paginated_data,
            'total_number_of_pages': total_number_of_pages,
            'total_number_of_items': total_number_of_invoices}

    return jsonify(data)


@app.route('/get_items_data')
def get_items_data():
    items = Item.query.all()
    json_items = [item.to_dict() for item in items]

    return jsonify(json_items)


@app.route('/update_item', methods=['POST'])
def update_item():
    if request.method == 'POST':
        try:
            item_id = request.form['item_id']
            item_to_update = db.session.query(Item).filter(Item.id == item_id).first()

            if item_to_update:
                # Modify the attributes
                item_to_update.title = request.form['title']
                item_to_update.description = request.form['description']
                item_to_update.price = request.form['price']

                db.session.commit()

                return jsonify(True)
            else:
                return jsonify(False)
        except Exception as e:
            application_modules.get_log_manager().warning(
                f"Exception occurred while trying to update item. Details: {e}")
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


def is_json_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() == 'json'
