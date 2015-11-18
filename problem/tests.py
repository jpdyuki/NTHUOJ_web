from django.test import TestCase, Client

from utils.test_helper import *

# Create your tests here.

class Tester(TestCase):

    def setUp(self):
        """ implements the interface of initializing django.test.TestCase """
        create_test_directory("./problem/test/")
        create_test_admin_user()
        create_test_judge_user()
        create_test_normal_user()
        self.ADMIN_USER = get_test_admin_user()
        self.ADMIN_CLIENT = get_test_admin_client()
        self.JUDGE_USER = get_test_judge_user()
        self.JUDGE_CLIENT = get_test_judge_client()
        self.NORMAL_USER = get_test_normal_user()
        self.NORMAL_CLIENT = get_test_normal_user_client()
        self.ANONYMOUS_CLIENT = Client()
