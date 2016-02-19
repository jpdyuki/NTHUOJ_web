from django.test import TestCase, Client
from django.core.urlresolvers import reverse

from problem.problem_info import get_problem_file_extension
from problem.models import Problem, Submission
from utils.test_helper import *


class Tester_Problem_new(TestCase):
    """ test view 'problem:new' """

    def setUp(self):
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

    def test_01_login(self):
        # 1.user does not login
        # Expectation: redirect to login page
        target_url = reverse('problem:new')
        redirect_url = reverse('users:login') + '?next=' + target_url
        response = self.ANONYMOUS_CLIENT.get(target_url)
        self.assertRedirects(response, redirect_url)

    def test_02_permission(self):
        # 2.user has no permission
        # Expectation: error 403
        target_url = reverse('problem:new')
        response = self.NORMAL_CLIENT.post(target_url)
        self.assertEqual(response.status_code, 403)

    def test_03_invalid_argument(self):
        # 3.using POST method but argument 'pname' is empty string
        # Expectation: redirect to view 'problem'
        target_url = reverse('problem:new')
        response = self.ADMIN_CLIENT.post(target_url, data={'pname':''})
        redirect_url = reverse('problem:problem')
        self.assertRedirects(response, redirect_url)

    def test_04_create_problem(self):
        # 4.argument 'pname' is not empty string
        # Expectation: create a new problem successfully and redirect to view 'edit'
        pname = random_word(20)
        target_url = reverse('problem:new')
        response = self.JUDGE_CLIENT.post(target_url, data={'pname':pname}, follow=True)
        pid = Problem.objects.all().order_by("-pk")[0].pk
        redirect_url = reverse('problem:edit', args=[pid])
        self.assertRedirects(response, redirect_url)
        self.assertEqual(response.context['problem'].pname, pname)


class Tester_Problem_detail(TestCase):
    """ test view 'problem:detail' """

    def setUp(self):
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

    def test_01_problem_not_found(self):
        """ test view 'detail' """
        # 1.problem does not exist
        # Expectation: error 404
        pid = 1000000
        target_url = reverse('problem:detail', args=[pid])
        response = self.ADMIN_CLIENT.get(target_url)
        self.assertEqual(response.status_code, 404)

    def test_02_permission(self):
        # 2.user has no permission
        # Expectation: error 403
        problem = create_problem(self.JUDGE_USER);
        target_url = reverse('problem:detail', args=[problem.pk])
        response = self.ANONYMOUS_CLIENT.get(target_url)
        self.assertEqual(response.status_code, 403)

    def test_03_show_detail(self):
        # 3.problem exists and user has permission
        # Expectation: show the detail of the problem
        problem = create_problem(self.JUDGE_USER);
        target_url = reverse('problem:detail', args=[problem.pk])
        response = self.JUDGE_CLIENT.get(target_url)
        self.assertEqual(response.context['problem'], problem)
