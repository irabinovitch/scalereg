# Django settings for scalereg project.

DEBUG = False
TEMPLATE_DEBUG = DEBUG

# Additional debug logging for sales transactions
# Set to True to enable.
SCALEREG_DEBUG_LOGGING_ENABLED = False
SCALEREG_DEBUG_LOGGING_PATH = '/tmp/scale_reg.log'

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # 'django.db.backends.mysql', 'django.db.backends.postgresql', 'django.db.backends.sqlite3', or 'django.db.backends.oracle'
        'NAME': '/CHANGE_THIS!!!!!__path_to/sqlite.db',  # Or path to database file if using sqlite3.
        'USER': '', # Not used with sqlite3.
        'PASSWORD': '',  # Not used with sqlite3.
        'HOST': '', # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '', # Set to empty string for default. Not used with sqlite3.
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Los_Angeles'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

# Absolute path to the directory that holds media.
# Example: '/home/media/media.lawrence.com/'
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: 'http://media.lawrence.com', 'http://example.com/media/'
MEDIA_URL = ''

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: 'http://foo.com/media/', '/media/'.
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'CHANGE_THIS!!!!!__ANY_VALID_PYTHON_STRING_WORKS'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.gzip.GZipMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

ROOT_URLCONF = 'scalereg.urls'

TEMPLATE_DIRS = (
    # Put strings here, like '/home/html/django_templates' or
    # 'C:/www/django/templates'.
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    '/CHANGE_THIS!!!!!__path_to/scalereg/scale_templates',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.messages.context_processors.messages',
    'django.contrib.auth.context_processors.auth',
)

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.sites',
    'scalereg.auth_helper',
    'scalereg.reg6',
    'scalereg.reports',
    'scalereg.simple_cfp',
    'scalereg.speaker_survey',
    'scalereg.sponsorship',
)

SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# It is highly recommended that you use reCAPTCHA to prevent spamming/attacks.
# It is turned off by default. To use reCAPTCHA, first get a reCAPTCHA account,
# then set SCALEREG_SIMPLECFP_USE_RECAPTCHA to True, and fill in the
# public/private keys.
# You will also need to install the Python reCAPTCHA client.
SCALEREG_SIMPLECFP_USE_RECAPTCHA = False
RECAPTCHA_PUBLIC_KEY = ''
RECAPTCHA_PRIVATE_KEY = ''

# Set to True if you want simple_cfp to be able to email speakers.
# You need to set EMAIL_HOST, EMAIL_PORT, and other EMAIL_ settings
# appropriately.
SCALEREG_SIMPLECFP_SEND_MAIL = False
# You also need to set the from address below:
SCALEREG_SIMPLECFP_EMAIL = ''

# MEDIA_ROOT and MEDIA_URL need to be set for uploads to work.
SCALEREG_SIMPLECFP_ALLOW_UPLOAD = False

# Secret used for speaker surveys to make survey URLs harder to guess.
SCALEREG_SPEAKERSURVEY_SECRET = 'CHANGE_THIS_IF_NEEDED'

# Optional questions about PGP keys for a PGP Key Signing Party.
#
# Integer value corresponding to the first PGP question. Set to -1 to disable.
# The questions must have consecutive IDs:
# Text: What is your PGP fingerprint?
# Text: What is your PGP fingerprint size? (number of bits)
# List: What is your PGP fingerprint type? / [DSA, RSA]
# Text: What is your second PGP fingerprint?
# Text: What is your second PGP fingerprint size? (number of bits)
# List: What is your second PGP fingerprint type? / [DSA, RSA]
# ...
SCALEREG_PGP_QUESTION_ID_START = -1

# Positive integer value indicating max number of PGP keys allowed.
SCALEREG_PGP_MAX_KEYS = 0

# The PGP Key Signing Party addon item name.
SCALEREG_PGP_KSP_ITEM_NAME = 'KSP'

# PayFlow Account Settings must be set to use PayFlow.
#
# PayFlow URL:
SCALEREG_PAYFLOW_URL = 'https://payflowlink.paypal.com/'
# Manager User Login:
SCALEREG_PAYFLOW_LOGIN = ''
# Partner (either Paypal or Verisign):
SCALEREG_PAYFLOW_PARTNER = ''

# Secret used for express check-in and scanned badges.
SCALEREG_EXPRESS_CHECKIN_SECRET = ''

# URL for the sponsorship agreement document.
SCALEREG_SPONSORSHIP_AGREEMENT_URL = 'CHANGE_THIS_URL'

# Set to True if you want scalereg to be able to email attendees.
# You need to set EMAIL_HOST, EMAIL_PORT, and other EMAIL_ settings
# appropriately.
SCALEREG_SEND_MAIL = False
# You also need to set the from address below:
SCALEREG_EMAIL = ''

# Increasing limit to work around Django bug with TemporaryFileUploadHandler.
#FILE_UPLOAD_MAX_MEMORY_SIZE = 20971520  # 20 MB
