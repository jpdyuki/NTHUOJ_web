from django.test import Client

import os


TEST_PATH = ""

def create_test_directory(dir_name):
    TEST_PATH = dir_name
    if not os.path.isdir(TEST_PATH):
        os.makedirs(TEST_PATH)
