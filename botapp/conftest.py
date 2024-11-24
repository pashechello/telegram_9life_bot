# botapp/conftest.py

import pytest
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

@pytest.fixture(scope="function")
def django_db_setup():
    from django.test import TransactionTestCase
    return TransactionTestCase()