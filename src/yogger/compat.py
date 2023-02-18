# Check if supported external packages are installed
# NOTE: These are not required, but will be used during formatting if found.
try:
    HAS_REQUESTS_PACKAGE = True
    from requests import Request, PreparedRequest, Response
    from requests.exceptions import RequestException
except (NameError, ModuleNotFoundError):
    HAS_REQUESTS_PACKAGE = False
