from django.test import TestCase, Client
from django.core.urlresolvers import reverse

from problem.models import Problem
from utils.test_helper import *


class Tester_Problem_testcase(TestCase):
    """ test view 'problem:testcase' """

    def setUp(self):
        create_test_directory()
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

    def tearDown(self):
        remove_test_directory()

    def test_01_login(self):
        # 1.user does not login
        # Expectation: redirect to login page
        pid = 1
        target_url = reverse('problem:testcase', args=[pid])
        redirect_url = reverse('users:login') + '?next=' + target_url
        response = self.ANONYMOUS_CLIENT.get(target_url)
        self.assertRedirects(response, redirect_url)

    def test_02_problem_not_found(self):
        # 2.problem does not exist
        # Expectation: error 404
        pid = 1000000
        target_url = reverse('problem:testcase', args=[pid])
        response = self.ADMIN_CLIENT.post(target_url)
        self.assertEqual(response.status_code, 404)

    def test_03_testcase_not_found(self):
        # 3.testcase does not exist
        # Expectation: error 404
        tid = 1000000
        problem = create_problem(self.JUDGE_USER)
        target_url = reverse('problem:testcase', args=[problem.pk, tid])
        response = self.ADMIN_CLIENT.post(target_url)
        self.assertEqual(response.status_code, 404)

    def test_04_testcase_misaligned(self):
        # 4.testcase does not belong to the problem
        # Expectation: error 404
        problem = create_problem(self.JUDGE_USER)
        fake_problem = create_problem(self.JUDGE_USER)
        testcase = create_testcase(fake_problem, local_files=False)
        target_url = reverse('problem:testcase', args=[problem.pk, testcase.pk])
        response = self.ADMIN_CLIENT.post(target_url)
        self.assertEqual(response.status_code, 404)

    def test_05_permission(self):
        # 5.user has no permission
        # Expectation: error 403
        problem = create_problem(self.JUDGE_USER)
        testcase = create_testcase(problem)
        target_url = reverse('problem:testcase', args=[problem.pk, testcase.pk])
        response = self.NORMAL_CLIENT.post(target_url)
        self.assertEqual(response.status_code, 404)

    def test_06_create_testcase(self):
        # 6.using POST method without argument 'tid', only 'time_limit' and 'memory_limit' are given
        # Expectation: create new testcase for this problem with given 'time_limit' and 'memory_limit'
        problem = create_problem(self.JUDGE_USER)
        target_url = reverse('problem:testcase', args=[problem.pk])
        data1 = {
            'time_limit': 3,
            'memory_limit': 12,
        }
        data2 = {
            'time_limit': 30,
            'memory_limit': 20,
        }
        response1 = self.JUDGE_CLIENT.post(target_url, data=data1)
        response2 = self.JUDGE_CLIENT.post(target_url, data=data2)
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response2.status_code, 200)
        testcases = Testcase.objects.filter(problem=problem).order_by('id')
        try:
            self.assertEqual(testcases[0].problem, problem)
            self.assertEqual(testcases[0].time_limit, data1['time_limit'])
            self.assertEqual(testcases[0].memory_limit, data1['memory_limit'])
            self.assertEqual(testcases[1].problem, problem)
            self.assertEqual(testcases[1].time_limit, data2['time_limit'])
            self.assertEqual(testcases[1].memory_limit, data2['memory_limit'])
        except IndexError:
            print "Failed to create new testcases for the problem..."
            self.assertTrue(False)

    def test_07_testcase_file_upload(self):
        # 7.using POST method, with arguments 'tid', 't_in' and 't_out'
        # Expectation: upload input and output files of the testcase to server
        problem = create_problem(self.JUDGE_USER)
        testcase = create_testcase(problem)
        target_url = reverse('problem:testcase', args=[problem.pk, testcase.pk])
        try:
            with open("%s%s.in" % (TEST_PATH, testcase.pk), 'r') as file_in,\
                 open("%s%s.out" % (TEST_PATH, testcase.pk), 'r') as file_out:
                    data = {
                        't_in': file_in,
                        't_out': file_out,
                    }
                    response = self.JUDGE_CLIENT.post(target_url, data=data)
        except IOError:
            print "Something went wrong when reading testcase files for testing..."
        compare_result = compare_local_and_uploaded_testcase_files(testcase.pk, testcase.pk)
        remove_testcase_file(testcase.pk, testcase.pk)
        self.assertTrue(compare_result)