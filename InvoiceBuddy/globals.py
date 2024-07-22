# General
APPLICATION_NAME = 'InvoiceBuddy'
APPLICATION_VERSION = '0.1.3'
JSON_RESPONSE_FORMAT_VERSION = 1

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
PAST_INVOICES_TABLE_ITEMS_PER_PAGE = 10
PAST_PROPOSALS_TABLE_ITEMS_PER_PAGE = 10
