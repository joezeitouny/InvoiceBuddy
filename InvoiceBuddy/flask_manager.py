import math
import time
import webbrowser
import plotly.graph_objects as go
from flask import render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_, func
from datetime import datetime, timedelta
from rich.console import Console
import json
import os
import qrcode

from InvoiceBuddy import app
from InvoiceBuddy import globals, utils
from InvoiceBuddy.log_manager import LogManager

db = SQLAlchemy(app)


class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100), nullable=False)
    customer_email = db.Column(db.String(100), nullable=True)
    customer_phone = db.Column(db.String(100), nullable=True)
    customer_address = db.Column(db.String(100), nullable=True)
    customer_country = db.Column(db.String(100), nullable=True)
    description = db.Column(db.Text, nullable=True)

    def to_dict(self):
        return dict(
            id=self.id,
            customer_name=self.customer_name,
            customer_email=self.customer_email,
            customer_phone=self.customer_phone,
            customer_address=self.customer_address,
            customer_country=self.customer_country,
            description=self.description
        )


class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(50), unique=True, nullable=False)
    invoice_date = db.Column(db.Date, nullable=False)
    invoice_type = db.Column(db.String(100), nullable=False)
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
            invoice_type=self.invoice_type,
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

        # If a seller logo file exists in the tmp folder then copy it to the static folder
        seller_logo_src_path = os.path.join(self._options.tmp_path, globals.SELLER_LOGO_FILENAME)
        if utils.check_file_exists(seller_logo_src_path):
            # Get the path of the static directory
            static_folder_path = app.static_folder

            # Get the absolute path of the static folder
            absolute_static_path = os.path.abspath(static_folder_path)
            seller_logo_dst_path = os.path.join(absolute_static_path, globals.SELLER_LOGO_FILENAME)
            utils.copy_file(src=seller_logo_src_path, dst=seller_logo_dst_path)

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
                # Store the uploaded JSON file on your server
                file.save(application_modules.get_options().configuration_path)
            except Exception as e:
                application_modules.get_log_manager().info(
                    f'Error while trying to update the configuration on the server. Details: {e}')
                return jsonify(False)
        else:
            return jsonify(False)

    return jsonify(True)


@app.route('/download_config')
def download_config():
    filename = application_modules.get_options().configuration_path

    try:
        with open(filename) as f:
            data = f.read()
    except Exception as e:
        application_modules.get_log_manager().info(
            f'Error while trying to read the configuration on the server. Details: {e}')
        return jsonify(False)

    return jsonify(data)


@app.route('/upload_seller_logo', methods=['POST'])
def upload_seller_logo():
    if 'seller_logo' in request.files:
        file = request.files['seller_logo']

        # Get the path of the static directory
        static_folder_path = app.static_folder

        # Get the absolute path of the static directory
        absolute_static_path = os.path.abspath(static_folder_path)
        seller_logo_src_path = os.path.join(absolute_static_path, globals.SELLER_LOGO_FILENAME)

        if file:
            try:
                # store the uploaded file in the application static folder
                file.save(str(seller_logo_src_path))

                # store the uploaded file in the tmp folder
                seller_logo_dst_path = os.path.join(application_modules.get_options().tmp_path,
                                                    globals.SELLER_LOGO_FILENAME)
                utils.copy_file(src=seller_logo_src_path, dst=seller_logo_dst_path)
            except Exception as e:
                application_modules.get_log_manager().info(
                    f'Error while trying to update the seller logo on the server. Details: {e}')
                return jsonify(False)

    return jsonify(True)


@app.route('/new_invoice_number')
def new_invoice_number():
    try:
        # Open the configuration JSON file
        with open(f'{application_modules.get_options().configuration_path}', 'r') as file:
            data = json.load(file)

        invoice_number = data['invoice']['invoice_number']
    except Exception as e:
        application_modules.get_log_manager().info(
            f'An unexpected error occurred while trying to retrieve a new invoice number. Details {e}')
        return -1

    return get_formatted_number(application_modules.get_options().invoice_prefix, invoice_number)


@app.route('/new_proposal_number')
def new_proposal_number():
    try:
        # Open the configuration JSON file
        with open(f'{application_modules.get_options().configuration_path}', 'r') as file:
            data = json.load(file)

        proposal_number = data['proposal']['proposal_number']
    except Exception as e:
        application_modules.get_log_manager().info(
            f'An unexpected error occurred while trying to retrieve a new proposal number. Details {e}')
        return -1

    return get_formatted_number(application_modules.get_options().proposal_prefix, proposal_number)


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


@app.route('/add_customer', methods=['POST'])
def add_customer():
    if request.method == 'POST':
        customer_data = {
            'name': request.form['customer_name'],
            'email': request.form['customer_email'],
            'phone': request.form['customer_phone'],
            'address': request.form['customer_address'],
            'country': request.form['customer_country'],
            'description': request.form['description']
        }

        new_customer = Customer(
            customer_name=customer_data['name'],
            customer_email=customer_data['email'],
            customer_phone=customer_data['phone'],
            customer_address=customer_data['address'],
            customer_country=customer_data['country'],
            description=customer_data['description'],
        )

        db.session.add(new_customer)
        db.session.commit()

        return jsonify(new_customer.id)


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
            'invoice_type': globals.InvoiceType.DEBIT.value,
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
            'status': globals.InvoiceStatus.UNPAID.value
        }

        new_invoice = Invoice(
            invoice_number=invoice_data['invoice_number'],
            invoice_date=invoice_data['invoice_date'],
            invoice_type=invoice_data['invoice_type'],
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

        if not update_invoice_number_in_configuration_file():
            return jsonify(False)

        return jsonify(new_invoice.id)


@app.route('/get_invoice', methods=['POST'])
def get_invoice():
    try:
        if request.method == 'POST':
            invoice_id = request.form['invoice_id']

            invoice = Invoice.query.filter(Invoice.id == invoice_id).first()

            return jsonify(invoice.to_dict())
    except Exception:
        return jsonify(False)

    return jsonify(False)


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
            'status': globals.ProposalStatus.UNACCEPTED.value
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


@app.route('/get_proposal', methods=['POST'])
def get_proposal():
    try:
        if request.method == 'POST':
            proposal_id = request.form['proposal_id']

            proposal = Proposal.query.filter(Proposal.id == proposal_id).first()

            return jsonify(proposal.to_dict())
    except Exception:
        return jsonify(False)

    return jsonify(False)


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
            'invoice_type': invoice.invoice_type,
            'due_date': invoice.due_date,
            'customer_name': invoice.customer_name,
            'reference_number': invoice.reference_number,
            'description': invoice.description.replace('\n', '<br>'),
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
            item['description'] = item.get('description', '').replace('\n', '<br>')

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
            'description': proposal.description.replace('\n', '<br>'),
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
            item['description'] = item.get('description', '').replace('\n', '<br>')

        return render_template('proposal_template.html', **proposal_data)


@app.route('/invoices')
def list_invoices():
    invoices = Invoice.query.all()
    json_invoices = [invoice.to_dict() for invoice in invoices]

    return jsonify(json_invoices)


@app.route('/active_invoices')
def list_active_invoices():
    invoices = Invoice.query.filter(Invoice.status == globals.InvoiceStatus.UNPAID.value).all()
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
    search = request.args.get('search', '')
    status = request.args.get('status', '')
    date = request.args.get('date', '')

    items_per_page = globals.PAST_INVOICES_TABLE_ITEMS_PER_PAGE

    # Start with the base query
    query = Invoice.query.filter(Invoice.status != globals.InvoiceStatus.UNPAID.value)

    # Apply filters
    if search:
        search = f"%{search}%"
        query = query.filter(or_(
            Invoice.invoice_number.ilike(search),
            Invoice.reference_number.ilike(search),
            Invoice.customer_name.ilike(search),
            Invoice.description.ilike(search)
        ))

    if status:
        query = query.filter(Invoice.status == int(status))

    if date:
        date_obj = datetime.strptime(date, '%Y-%m-%d').date()
        query = query.filter(func.date(Invoice.invoice_date) == date_obj)

    # Get total count for pagination
    total_invoices = query.count()

    # Calculate the sum of totals for the filtered invoices
    total_sum = query.with_entities(func.sum(Invoice.total_amount)).scalar() or 0

    # Apply pagination
    start_idx = (page - 1) * items_per_page
    invoices = query.order_by(Invoice.invoice_date.desc()).offset(start_idx).limit(items_per_page).all()

    paginated_data = [invoice.to_dict() for invoice in invoices]

    total_number_of_pages = math.ceil(total_invoices / items_per_page)

    data = {
        'past_invoices': paginated_data,
        'total_number_of_pages': total_number_of_pages,
        'total_number_of_invoices': total_invoices,
        'total_sum': round(total_sum, 2)  # Rounding to 2 decimal places
    }

    return jsonify(data)


@app.route('/past_invoices_count')
def past_invoices_count():
    invoices = Invoice.query.filter(Invoice.status != globals.InvoiceStatus.UNPAID.value).all()

    return jsonify(len(invoices))


@app.route('/proposals')
def list_proposals():
    proposals = Proposal.query.all()
    json_proposals = [proposal.to_dict() for proposal in proposals]

    return jsonify(json_proposals)


@app.route('/active_proposals')
def list_active_proposals():
    proposals = Proposal.query.filter(Proposal.status == globals.ProposalStatus.UNACCEPTED.value).all()
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
    search = request.args.get('search', '')
    status = request.args.get('status', '')
    date = request.args.get('date', '')

    items_per_page = globals.PAST_PROPOSALS_TABLE_ITEMS_PER_PAGE

    # Start with the base query
    query = Proposal.query.filter(Proposal.status != globals.ProposalStatus.UNACCEPTED.value)

    # Apply filters
    if search:
        search = f"%{search}%"
        query = query.filter(or_(
            Proposal.proposal_number.ilike(search),
            Proposal.reference_number.ilike(search),
            Proposal.customer_name.ilike(search),
            Proposal.description.ilike(search)
        ))

    if status:
        query = query.filter(Proposal.status == int(status))

    if date:
        date_obj = datetime.strptime(date, '%Y-%m-%d').date()
        query = query.filter(func.date(Proposal.proposal_date) == date_obj)

    # Get total count for pagination
    total_proposals = query.count()

    # Calculate the sum of totals for the filtered invoices
    total_sum = query.with_entities(func.sum(Proposal.total_amount)).scalar() or 0

    # Apply pagination
    start_idx = (page - 1) * items_per_page
    proposals = query.order_by(Proposal.proposal_date.desc()).offset(start_idx).limit(items_per_page).all()

    paginated_data = [proposal.to_dict() for proposal in proposals]

    total_number_of_pages = math.ceil(total_proposals / items_per_page)

    data = {
        'past_proposals': paginated_data,
        'total_number_of_pages': total_number_of_pages,
        'total_number_of_proposals': total_proposals,
        'total_sum': round(total_sum, 2)  # Rounding to 2 decimal places
    }

    return jsonify(data)


@app.route('/past_proposals_count')
def past_proposals_count():
    proposals = Proposal.query.filter(Proposal.status != globals.ProposalStatus.UNACCEPTED.value).all()

    return jsonify(len(proposals))


@app.route('/delete_customer', methods=['POST'])
def delete_customer():
    if request.method == 'POST':
        try:
            customer_id = request.form['customer_id']

            customer_to_delete = db.session.query(Customer).filter_by(id=customer_id).one()
            db.session.delete(customer_to_delete)
            db.session.commit()

            return jsonify(True)
        except Exception as e:
            application_modules.get_log_manager().warning(
                f"Exception occurred while trying to delete customer. Details: {e}")
            return jsonify(False)

    return jsonify(False)


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
            invoice.status = globals.InvoiceStatus.CANCELED.value

            # create a new debit invoice
            new_number = new_invoice_number()
            new_invoice = Invoice(
                invoice_number=new_number,
                invoice_date=invoice.invoice_date,
                invoice_type=globals.InvoiceType.CREDIT.value,
                due_date=invoice.due_date,
                customer_name=invoice.customer_name,
                reference_number=invoice.reference_number,
                description=invoice.description,
                items=invoice.items,
                total_amount=invoice.total_amount * -1,
                seller_name=invoice.seller_name,
                seller_address=invoice.seller_address,
                seller_country=invoice.seller_country,
                seller_phone=invoice.seller_phone,
                seller_email=invoice.seller_email,
                seller_iban=invoice.seller_iban,
                seller_bic=invoice.seller_bic,
                seller_paypal_address=invoice.seller_paypal_address,
                currency_symbol=invoice.currency_symbol,
                currency_name=invoice.currency_name,
                invoice_terms_and_conditions=invoice.invoice_terms_and_conditions,
                status=globals.InvoiceStatus.PAID.value
            )

            db.session.add(new_invoice)
            db.session.commit()

            if not update_invoice_number_in_configuration_file():
                raise Exception("Could not update invoice number in configuration file!")

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
            invoice.status = globals.InvoiceStatus.PAID.value
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
            proposal.status = globals.ProposalStatus.REJECTED.value

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
            proposal.status = globals.ProposalStatus.ACCEPTED.value

            # create a new invoice from the accepted proposal
            invoice_number = new_invoice_number()
            new_invoice = Invoice(
                invoice_number=invoice_number,
                invoice_date=datetime.now(),
                invoice_type=globals.InvoiceType.DEBIT.value,
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
                status=globals.InvoiceStatus.UNPAID.value
            )
            db.session.add(new_invoice)
            db.session.commit()

            return jsonify(True)
        except Exception as e:
            application_modules.get_log_manager().warning(
                f"Exception occurred while trying to mark proposal as accepted. Details: {e}")
            return jsonify(False)

    return jsonify(False)


@app.route('/view_customers')
def view_customers():
    # Get application name and version
    application_name = utils.get_application_name()
    application_version = utils.get_application_version()
    invoice_valid_for_days = application_modules.get_options().invoice_valid_for_days
    proposal_valid_for_days = application_modules.get_options().proposal_valid_for_days
    currency_symbol = application_modules.get_options().currency_symbol
    currency_name = application_modules.get_options().currency_name

    return render_template('customers.html', application_name=application_name,
                           application_version=application_version, invoice_valid_for_days=invoice_valid_for_days,
                           proposal_valid_for_days=proposal_valid_for_days, currency_symbol=currency_symbol,
                           currency_name=currency_name)


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


@app.route('/customers')
def list_customers():
    page = int(request.args.get('page', 1))
    items_per_page = globals.CUSTOMERS_ITEMS_PER_PAGE

    start_idx = (page - 1) * items_per_page
    end_idx = start_idx + items_per_page

    customers = Customer.query.all()
    paginated_data = [customer.to_dict() for customer in customers[start_idx:end_idx]]

    for item in paginated_data:
        item['description'] = item['description'].replace('\n', '<br>')

    total_number_of_pages = math.floor(len(customers) / items_per_page)
    if len(customers) % items_per_page != 0:
        total_number_of_pages += 1

    total_number_of_customers = len(customers)

    data = {'customers': paginated_data,
            'total_number_of_pages': total_number_of_pages,
            'total_number_of_customers': total_number_of_customers}

    return jsonify(data)


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

    total_number_of_items = len(items)

    data = {'items': paginated_data,
            'total_number_of_pages': total_number_of_pages,
            'total_number_of_items': total_number_of_items}

    return jsonify(data)


@app.route('/get_customers_data')
def get_customers_data():
    customers = Customer.query.all()
    json_customers = [customer.to_dict() for customer in customers]

    return jsonify(json_customers)


@app.route('/get_items_data')
def get_items_data():
    items = Item.query.all()
    json_items = [item.to_dict() for item in items]

    return jsonify(json_items)


@app.route('/update_customer', methods=['POST'])
def update_customer():
    if request.method == 'POST':
        try:
            customer_id = request.form['customer_id']
            customer_to_update = db.session.query(Customer).filter(Customer.id == customer_id).first()

            if customer_to_update:
                # Modify the attributes
                customer_to_update.customer_name = request.form['customer_name']
                customer_to_update.customer_email = request.form['customer_email']
                customer_to_update.customer_phone = request.form['customer_phone']
                customer_to_update.customer_address = request.form['customer_address']
                customer_to_update.customer_country = request.form['customer_country']
                customer_to_update.description = request.form['description']

                db.session.commit()

                return jsonify(True)
            else:
                return jsonify(False)
        except Exception as e:
            application_modules.get_log_manager().warning(
                f"Exception occurred while trying to update item. Details: {e}")
            return jsonify(False)

    return jsonify(False)


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


def update_invoice_number_in_configuration_file():
    try:
        # Open the configuration JSON file
        with open(f'{application_modules.get_options().configuration_path}', 'r') as file:
            data = json.load(file)

        invoice_number = data['invoice']['invoice_number']
        data['invoice']['invoice_number'] = utils.try_parse_int(invoice_number) + 1

        with open(f'{application_modules.get_options().configuration_path}', 'w') as file:
            json.dump(data, file, indent=4)
    except Exception as e:
        application_modules.get_log_manager().info(
            f'An unexpected error occurred while trying to save a new invoice number. Details {e}')
        return False

    return True


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


# Define a function to generate the graph for total amounts per month
def get_total_amounts_per_month(invoices):
    months = []
    amounts = []
    for invoice in invoices:
        month = invoice.invoice_date.strftime('%Y-%m')
        if month not in months:
            months.append(month)
            amounts.append(0)
        i = months.index(month)
        amounts[i] += invoice.total_amount
    return months, amounts


# Define a function to generate the graph for total amounts per trimester
def get_total_amounts_per_trimester(invoices):
    trimesters = []
    amounts = []
    for invoice in invoices:
        month = datetime.strptime(invoice.invoice_date.strftime('%Y-%m'), '%Y-%m').month
        if 1 <= month <= 3:
            quarter = 'Q1'
        elif 4 <= month <= 6:
            quarter = 'Q2'
        elif 7 <= month <= 9:
            quarter = 'Q3'
        else:
            quarter = 'Q4'
        if quarter not in trimesters:
            trimesters.append(quarter)
            amounts.append(0)
        i = trimesters.index(quarter)
        amounts[i] += invoice.total_amount
    return trimesters, amounts


# Define a function to generate the graph for total amounts per semester
def get_total_amounts_per_semester(invoices):
    semesters = []
    amounts = []
    for invoice in invoices:
        month = datetime.strptime(invoice.invoice_date.strftime('%Y-%m'), '%Y-%m').month
        if 1 <= month <= 6:
            semester = 'S1'
        else:
            semester = 'S2'
        if semester not in semesters:
            semesters.append(semester)
            amounts.append(0)
        i = semesters.index(semester)
        amounts[i] += invoice.total_amount
    return semesters, amounts


# Define a function to generate the graph for total amounts per year
def get_total_amounts_per_year(invoices):
    years = []
    amounts = []
    for invoice in invoices:
        year = invoice.invoice_date.year
        if year not in years:
            years.append(year)
            amounts.append(0)
        i = years.index(year)
        amounts[i] += invoice.total_amount
    return years, amounts


# Define a function to generate the graph for amount breakdown by status
def get_breakdown_by_status(invoices):
    paid = 0
    unpaid = 0
    canceled = 0
    for invoice in invoices:
        if invoice.status == globals.InvoiceStatus.PAID.value:  # Paid
            paid += 1
        elif invoice.status == globals.InvoiceStatus.UNPAID.value:  # Unpaid
            unpaid += 1
        elif invoice.status == globals.InvoiceStatus.CANCELED.value:  # Canceled
            canceled += 1
    return [f'Paid ({paid})', f'Unpaid ({unpaid})', f'Canceled ({canceled})'], [paid, unpaid, canceled]


@app.route('/view_stats', methods=['GET'])
def view_stats():
    # Get application name and version
    application_name = utils.get_application_name()
    application_version = utils.get_application_version()
    invoice_valid_for_days = application_modules.get_options().invoice_valid_for_days
    proposal_valid_for_days = application_modules.get_options().proposal_valid_for_days
    currency_symbol = application_modules.get_options().currency_symbol
    currency_name = application_modules.get_options().currency_name

    return render_template('stats.html', application_name=application_name,
                           application_version=application_version, invoice_valid_for_days=invoice_valid_for_days,
                           proposal_valid_for_days=proposal_valid_for_days, currency_symbol=currency_symbol,
                           currency_name=currency_name)


@app.route('/get_stats', methods=['GET'])
def get_stats():
    invoices = Invoice.query.all()
    months, amounts_month = get_total_amounts_per_month(invoices)
    trimesters, amounts_trimester = get_total_amounts_per_trimester(invoices)
    semesters, amounts_semester = get_total_amounts_per_semester(invoices)
    years, amounts_year = get_total_amounts_per_year(invoices)
    breakdown, breakdown_values = get_breakdown_by_status(invoices)

    # Create the graph for total amounts per month
    fig1 = go.Figure(data=[go.Bar(x=months, y=amounts_month)])
    fig1.update_layout(title='Total Amounts per Month', xaxis_title='Month', yaxis_title='Amount')

    # Create the graph for total amounts per trimester
    fig2 = go.Figure(data=[go.Bar(x=trimesters, y=amounts_trimester)])
    fig2.update_layout(title='Total Amounts per Trimester', xaxis_title='Trimester', yaxis_title='Amount')

    # Create the graph for total amounts per semester
    fig3 = go.Figure(data=[go.Bar(x=semesters, y=amounts_semester)])
    fig3.update_layout(title='Total Amounts per Semester', xaxis_title='Semester', yaxis_title='Amount')

    # Create the graph for total amounts per year
    fig4 = go.Figure(data=[go.Bar(x=years, y=amounts_year)])
    fig4.update_layout(title='Total Amounts per Year', xaxis_title='Year', yaxis_title='Amount')

    # Create the graph for amount breakdown by status
    fig5 = go.Figure(data=[go.Pie(labels=breakdown, values=breakdown_values)])
    fig5.update_layout(title='Amount Breakdown by Status')

    # Return the graphs as a JSON response
    return jsonify({'fig1': fig1.to_json(), 'fig2': fig2.to_json(), 'fig3': fig3.to_json(), 'fig4': fig4.to_json(),
                    'fig5': fig5.to_json()})
