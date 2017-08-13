#!/usr/bin/env python
import os
import sys

from gamifiededucation.helper import load_to_environment

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gamifiededucation.settings")
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    local_env_path = os.path.join(base_dir, 'local.env')
    load_to_environment(local_env_path)

    try:
        from django.core.management import execute_from_command_line
    except ImportError:
        # The above import may fail for some other reason. Ensure that the
        # issue is really that Django is missing to avoid masking other
        # exceptions on Python 2.
        try:
            import django
        except ImportError:
            raise ImportError(
                "Couldn't import Django. Are you sure it's installed and "
                "available on your PYTHONPATH environment variable? Did you "
                "forget to activate a virtual environment?"
            )
        raise
    execute_from_command_line(sys.argv)
