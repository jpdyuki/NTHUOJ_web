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

def create_test_admin_user():
    username = "test_admin"
    password = "test_admin"
    user_level = User.ADMIN
    create_test_user(username, password, user_level)

def create_test_judge_user():
    username = "test_judge"
    password = "test_judge"
    user_level = User.JUDGE
    create_test_user(username, password, user_level)

def create_test_normal_user():
    username = "test_user"
    password = "test_user"
    user_level = User.USER
    create_test_user(username, password, user_level)

def get_test_admin_user():
    return User.objects.get(username="test_admin")

def get_test_judge_user():
    return User.objects.get(username="test_judge")

def get_test_normal_user():
    return User.objects.get(username="test_user")

def get_test_admin_client():
    test_admin_client = Client()
    test_admin_client.login(username="test_admin", password="test_admin")
    return test_admin_client

def get_test_judge_client():
    test_judge_client = Client()
    test_judge_client.login(username="test_judge", password="test_judge")
    return test_judge_client

def get_test_normal_user_client():
    test_user_client = Client()
    test_user_client.login(username="test_user", password="test_user")
    return test_user_client