from django.test import Client

import os

from users.models import User


TEST_PATH = ""

def create_test_directory(dir_name):
    TEST_PATH = dir_name
    if not os.path.isdir(TEST_PATH):
        os.makedirs(TEST_PATH)

def create_test_user(username, password, user_level):
    test_user = User.objects.create_user(username, password)
    test_user.user_level = user_level
    test_user.is_active = True
    test_user.save()