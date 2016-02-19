from django.test import TestCase, Client
from django.core.urlresolvers import reverse

from problem.models import Problem
from utils.test_helper import *


class Tester_Problem_tag(TestCase):
    """ test view 'problem:tag' """

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
        pid = 1
        target_url = reverse('problem:tag', args=[pid])
        redirect_url = reverse('users:login') + '?next=' + target_url
        response = self.ANONYMOUS_CLIENT.get(target_url)
        self.assertRedirects(response, redirect_url)

    def test_02_problem_not_found(self):
        # 2.problem does not exist
        # Expectation: error 404
        pid = 1
        target_url = reverse('problem:tag', args=[pid])
        data = {
            'tag_name': random_word(10),
        }
        response = self.ADMIN_CLIENT.post(target_url, data=data)
        self.assertEqual(response.status_code, 404)

    def test_03_create_tag(self):
        # 5.problem exists
        # Expectation: create a new tag for this problem with the following constraint
        #              a) duplicate or empty string is not allowed to be added
        #              b) the string whose length is over 20 will be truncated
        problem = create_problem(self.JUDGE_USER)
        target_url = reverse('problem:tag', args=[problem.pk])
        tag_names = ['nthuoj', 'ggqaq', 'ggqaqXDD', '', 'nthuoj', '01234567899876543210END']
        for i in range(2):
            self.ADMIN_CLIENT.post(target_url, data={'tag_name':tag_names[i]})
        for i in range(2,4):
            self.JUDGE_CLIENT.post(target_url, data={'tag_name':tag_names[i]})
        for i in range(4,6):
            self.NORMAL_CLIENT.post(target_url, data={'tag_name':tag_names[i]})
        results = [tag.tag_name for tag in problem.tags.all()]
        expectations = ['nthuoj', 'ggqaq', 'ggqaqXDD', '01234567899876543210']
        self.assertEqual(problem.tags.count(), 4)
        self.assertTrue(set(results)==set(expectations))


class Tester_Problem_delete_tag(TestCase):
    """ test view 'problem:delete_tag' """

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
        pid = 1
        tag_id = 1
        target_url = reverse('problem:delete_tag', args=[pid, tag_id])
        redirect_url = reverse('users:login') + '?next=' + target_url
        response = self.ANONYMOUS_CLIENT.get(target_url)
        self.assertRedirects(response, redirect_url)

    def test_02_problem_not_found(self):
        # 2.problem does not exist
        # Expectation: error 404
        pid = 1000000
        tag_id = 1
        target_url = reverse('problem:delete_tag', args=[pid, tag_id])
        response = self.ADMIN_CLIENT.get(target_url)
        self.assertEqual(response.status_code, 404)

    def test_03_tag_not_found(self):
        # 3.tag does not exist
        # Expectation: error 404
        problem = create_problem(self.JUDGE_USER)
        tag_id = 1000000
        target_url = reverse('problem:delete_tag', args=[problem.pk, tag_id])
        response = self.JUDGE_CLIENT.get(target_url)
        self.assertEqual(response.status_code, 404)

    def test_04_permission(self):
        # 4.user has no permission
        # Expectation: error 403
        problem = create_problem(self.JUDGE_USER)
        tag = create_tag('testTag', problem)
        target_url = reverse('problem:delete_tag', args=[problem.pk, tag.pk])
        response = self.NORMAL_CLIENT.get(target_url)
        self.assertEqual(response.status_code, 403)

    def test_05_tag_misalign(self):
        # 5.tag does not belong to the problem
        # Expectation: nothing changed
        problem = create_problem(self.JUDGE_USER)
        tag = create_tag('greedy', problem)
        another_problem = create_problem(self.JUDGE_USER)
        tag_another = create_tag('greedy', another_problem)
        target_url = reverse('problem:delete_tag', args=[problem.pk, tag_another.pk])
        response = self.ADMIN_CLIENT.get(target_url)
        self.assertEquals(problem.tags.count(), 1)
        self.assertEquals(another_problem.tags.count(), 1)

    def test_06_delete_tag(self):
        # 6.tag belongs to the problem
        # Expectation: remove the tag from the problem
        problem = create_problem(self.JUDGE_USER)
        tag_names = ['nthuoj', 'ggqaq', 'ggqaqXDD', '01234567899876543210']
        tags = []
        for i in range(4):
            new_tag = create_tag(tag_names[i], problem)
            tags.append(new_tag)
        for i in [1, 2]:
            target_url = reverse('problem:delete_tag', args=[problem.pk, tags[i].pk])
            response = self.ADMIN_CLIENT.get(target_url)
        results = [tag.tag_name for tag in problem.tags.all()]
        expectations = ['nthuoj', '01234567899876543210']
        self.assertEquals(problem.tags.count(), 2)
        self.assertTrue(set(results)==set(expectations))
