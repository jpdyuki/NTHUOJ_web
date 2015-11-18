from django.test import TestCase, Client
from django.core.urlresolvers import reverse

from problem.problem_info import *
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

    def test_01_new(self):
        """ test view 'new' """
        target_url = reverse('problem:new')

        # 1.user does not login
        # Expectation: redirect to login page
        redirect_url = reverse('users:login') + '?next=' + target_url
        response = self.ANONYMOUS_CLIENT.get(target_url)
        self.assertRedirects(response, redirect_url)

        # 2.without using POST method
        # Expectation: redirect to view 'problem'
        response = self.ADMIN_CLIENT.get(target_url)
        redirect_url = reverse('problem:problem')
        self.assertRedirects(response, redirect_url)

        # 3.using POST method, but user has no permission
        # Expectation: error 403
        response = self.NORMAL_CLIENT.post(target_url)
        self.assertContains(response, "No Permission to Access.", status_code=403)

        # 4.using POST method without argument 'pname'
        # Expectation: redirect to view 'problem'
        response = self.ADMIN_CLIENT.post(target_url)
        redirect_url = reverse('problem:problem')
        self.assertRedirects(response, redirect_url)

        # 5.using POST method but argument 'pname' is empty string
        # Expectation: redirect to view 'problem'
        response = self.ADMIN_CLIENT.post(target_url, data={'pname':''})
        redirect_url = reverse('problem:problem')
        self.assertRedirects(response, redirect_url)

        # 6.using POST method and argument 'pname' is not empty string
        # Expectation: create new problem successfully and redirect to view 'edit'
        pid = 1
        pname = 'testProblem'
        response = self.JUDGE_CLIENT.post(target_url, data={'pname':pname}, follow=True)
        redirect_url = reverse('problem:edit', args=[pid])
        self.assertRedirects(response, redirect_url)
        self.assertEqual(response.context['problem'].pname, pname)

    def test_02_detail(self):
        """ test view 'detail' """
        # 1.problem does not exist
        # Expectation: error 404
        pid = 1
        target_url = reverse('problem:detail', args=[pid])
        response = self.ADMIN_CLIENT.get(target_url)
        self.assertContains(response, "problem %d does not exist" % (pid), status_code=404)

        # 2.user has no permission
        # Expectation: error 403
        problem = create_problem('testProblem', self.JUDGE_USER);
        target_url = reverse('problem:detail', args=[problem.pk])
        response = self.ANONYMOUS_CLIENT.get(target_url)
        self.assertContains(response, "No Permission to Access.", status_code=403)

        # 3.problem exists and user has permission
        # Expectation: render view 'detail' with the problem requested
        problem = create_problem('testProblem', self.JUDGE_USER);
        target_url = reverse('problem:detail', args=[problem.pk])
        response = self.JUDGE_CLIENT.get(target_url)
        self.assertEqual(response.context['problem'], problem)

    def test_03_delete_problem(self):
        """ test view 'delete_problem' """
        # 1.user does not login
        # Expectation: redirect to login page
        pid = 1
        target_url = reverse('problem:delete_problem', args=[pid])
        redirect_url = reverse('users:login') + '?next=' + target_url
        response = self.ANONYMOUS_CLIENT.get(target_url)
        self.assertRedirects(response, redirect_url)

        # 2.problem does not exist
        # Expectation: error 404
        pid = 1
        target_url = reverse('problem:delete_problem', args=[pid])
        response = self.ADMIN_CLIENT.get(target_url)
        self.assertContains(response, "problem %d does not exist" % (pid), status_code=404)

        # 3.user has no permission
        # Expectation: error 403
        problem = create_problem('testProblem', self.ADMIN_USER);
        target_url = reverse('problem:delete_problem', args=[problem.pk])
        response = self.JUDGE_CLIENT.get(target_url)
        self.assertContains(response, "No Permission to Access.", status_code=403)

        # 4.problem exists and user has permission
        # Expectation: delete problem successfully and redirect to view 'problem'
        redirect_url = reverse('problem:problem')
        response = self.ADMIN_CLIENT.get(target_url)
        self.assertRedirects(response, redirect_url)
        response = self.ADMIN_CLIENT.get(target_url)
        self.assertContains(response, "problem %d does not exist" % (problem.pk), status_code=404)

    def test_05_testcase(self):
        """ test view 'testcase' """
        # 1.user does not login
        # Expectation: redirect to login page
        pid = 1
        target_url = reverse('problem:testcase', args=[pid])
        redirect_url = reverse('users:login') + '?next=' + target_url
        response = self.ANONYMOUS_CLIENT.get(target_url)
        self.assertRedirects(response, redirect_url)

        # 2.without using POST method
        # Expectation: empty HttpResponse
        pid = 1
        target_url = reverse('problem:testcase', args=[pid])
        response = self.ADMIN_CLIENT.get(target_url)
        self.assertEqual(response.content, "")

        # 3.problem does not exist
        # Expectation: error 404
        pid = 1
        target_url = reverse('problem:testcase', args=[pid])
        response = self.ADMIN_CLIENT.post(target_url)
        self.assertContains(response, "problem %d does not exist" % (pid), status_code=404)

        # 4.testcase does not exist
        # Expectation: error 404
        tid = 1
        problem = create_problem('testProblem', self.JUDGE_USER)
        target_url = reverse('problem:testcase', args=[problem.pk, tid])
        response = self.ADMIN_CLIENT.post(target_url)
        self.assertContains(response, "testcase %d does not exist" % (tid), status_code=404)

        # 5.testcase does not belong to the problem
        problem = create_problem('testProblem', self.JUDGE_USER)
        fake_problem = create_problem('testProblem', self.JUDGE_USER)
        testcase = create_testcase(fake_problem, 1, 32, local_files=False)
        target_url = reverse('problem:testcase', args=[problem.pk, testcase.pk])
        response = self.ADMIN_CLIENT.post(target_url)
        self.assertContains(response,
                            "testcase %d does not belong to problem %d" % (testcase.pk, problem.pk),
                            status_code=404)

        # 6.user has no permission
        # Expectation: error 403
        problem = create_problem('testProblem', self.JUDGE_USER)
        testcase = create_testcase(problem, 1, 32)
        target_url = reverse('problem:testcase', args=[problem.pk, testcase.pk])
        response = self.NORMAL_CLIENT.post(target_url)
        self.assertContains(response, "No Permission to Access.", status_code=403)

        # 7.using POST method without argument 'tid', but 'time_limit' and 'memory_limit'
        # Expectation: create new testcase for this problem with given 'time_limit' and 'memory_limit'
        problem = create_problem('testProblem', self.JUDGE_USER)
        target_url = reverse('problem:testcase', args=[problem.pk])
        data1 = {
            'time_limit': 3,
            'memory_limit': 12 }
        data2 = {
            'time_limit': 30,
            'memory_limit': 20}
        response1 = self.JUDGE_CLIENT.post(target_url, data=data1)
        response2 = self.JUDGE_CLIENT.post(target_url, data=data2)
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response2.status_code, 200)
        testcases = get_testcase(problem)
        try:
            self.assertEqual(testcases[0].problem, problem)
            self.assertEqual(testcases[0].time_limit, 3)
            self.assertEqual(testcases[0].memory_limit, 12)
            self.assertEqual(testcases[1].problem, problem)
            self.assertEqual(testcases[1].time_limit, 30)
            self.assertEqual(testcases[1].memory_limit, 20)
        except IndexError:
            print "Failed to create new testcases for the problem..."
            self.assertTrue(False)

        # 8.using POST method, with arguments 'tid', 't_in' and 't_out'
        # Expectation: upload input and output files of testcase to server
        problem = create_problem('testProblem', self.JUDGE_USER)
        testcase = create_testcase(problem, 1, 32)
        target_url = reverse('problem:testcase', args=[problem.pk, testcase.pk])
        try:
            with open("%s%s.in" % (TEST_PATH, testcase.pk), 'r') as file_in,\
                 open("%s%s.out" % (TEST_PATH, testcase.pk), 'r') as file_out:
                    data = {
                        't_in': file_in,
                        't_out': file_out}
                    response = self.JUDGE_CLIENT.post(target_url, data=data)
        except IOError:
            print "Something went wrong when reading testcase files for testing..."
        compare_result = compare_local_and_uploaded_testcase_files(testcase.pk, testcase.pk)
        remove_testcase_file(testcase.pk, testcase.pk)
        self.assertContains(response, "tid", status_code=200)
        self.assertTrue(compare_result)