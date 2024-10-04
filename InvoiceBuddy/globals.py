from enum import Enum

# General
APPLICATION_NAME = 'InvoiceBuddy'
APPLICATION_VERSION = '0.2.21'
JSON_RESPONSE_FORMAT_VERSION = 1
SELLER_LOGO_FILENAME = "seller-logo.png"
INVOICE_TEMPLATE_FILENAME = "invoice_template.html"
PROPOSAL_TEMPLATE_FILENAME = "proposal_template.html"
INTERNAL_SERVER_ERROR = "An error occurred on the server. Please check the server logs for more details"

# Caching
FLASK_WEB_SERVER_CACHE_INTERVAL = 5    # in seconds

# Logging
LOG_FILENAME = 'InvoiceBuddy.log'
LOG_FILE_SIZE = 1024 * 1024  # Log file size 1MB
LOGGER_NAME = 'InvoiceBuddy'

# DB
DATABASE_NAME = "InvoiceBuddy"
INVOICE_FOLDER = "invoices"
PROPOSAL_FOLDER = "proposals"

# Presentation
ITEMS_ITEMS_PER_PAGE = 10
CUSTOMERS_ITEMS_PER_PAGE = 10
PAST_INVOICES_TABLE_ITEMS_PER_PAGE = 10
PAST_PROPOSALS_TABLE_ITEMS_PER_PAGE = 10


# Invoices
class InvoiceType(Enum):
    CREDIT = 'credit'
    DEBIT = 'debit'


class InvoiceStatus(Enum):
    UNPAID = 0
    PAID = 1
    CANCELED = 2


# Proposals
class ProposalStatus(Enum):
    UNACCEPTED = 0
    ACCEPTED = 1
    REJECTED = 2
