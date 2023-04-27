"""Optional dependencies.

This module contains optional dependencies that are not required for the
package to function, but will be used if found.
"""

# Check if supported external packages are installed
# NOTE: These are not required, but will be used during formatting if found.
try:
    HAS_REQUESTS_PACKAGE = True
    from requests import (
        PreparedRequest,
        Request,
        Response,
    )
    from requests.exceptions import RequestException
except (NameError, ModuleNotFoundError):
    HAS_REQUESTS_PACKAGE = False
