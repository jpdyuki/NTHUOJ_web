from django.test import TestCase, Client
from django.core.urlresolvers import reverse

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
