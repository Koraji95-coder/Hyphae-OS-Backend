import os
from dotenv import load_dotenv

# Load .env file into environment automatically (if it exists in project root)
load_dotenv()

def get_env_variable(key: str, default=None, optional=True):
    """
    get_env_variable() 🔍

    Attempts to load an environment variable from the system or `.env` file.

    Args:
        key (str): The name of the environment variable.
        default (any): A fallback value if the variable is missing.
        optional (bool): If False and the key is missing, raise a KeyError.

    Returns:
        str | any: The environment variable value, or fallback/default.

    Raises:
        KeyError: If the variable is required but missing and no default is given.
    """
    value = os.environ.get(key, default)
    if value is None and not optional:
        raise KeyError(f"❌ Required environment variable '{key}' is missing.")
    return value

def is_test_env():
    """
    is_test_env() 🧪

    Returns True if ENVIRONMENT=test, used to toggle test stubs.
    """
    return os.environ.get("ENVIRONMENT", "").lower() == "test"

def is_dev_env():
    """
    is_dev_env() 🛠️

    Returns True if ENVIRONMENT=development, used to enable debug flags/logs.
    """
    return os.environ.get("ENVIRONMENT", "").lower() == "development"