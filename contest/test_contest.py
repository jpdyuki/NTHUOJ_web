from django.test import TestCase, Client
from django.core.urlresolvers import reverse

from datetime import datetime, timedelta

from contest.models import Contest
from utils.test_helper import *


class Tester_Contest_new(TestCase):
    """ test view 'contest:new' """

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
        target_url = reverse('contest:new')
        redirect_url = reverse('users:login') + '?next=' + target_url
        response = self.ANONYMOUS_CLIENT.post(target_url)
        self.assertRedirects(response, redirect_url)

    def test_02_permission(self):
    	# 2.user has no permission
        # Expectation: error 403
        target_url = reverse('contest:new')
        response = self.NORMAL_CLIENT.post(target_url)
        self.assertEqual(response.status_code, 403)

    def test_03_invalid_form_01(self):
        # 3.user has permission but the form is invalid (start_time < end_time)
        # Expectation: failed to create a new contest
        target_url = reverse('contest:new')
        start_time = datetime.now()
        end_time = datetime.now() + timedelta(days=-1)
        data = POST_data_of_editing_Contest(
            self.JUDGE_USER, start_time=start_time, end_time=end_time)
        contest_num_before = Contest.objects.count()
        response = self.JUDGE_CLIENT.post(target_url, data=data)
        contest_num_current = Contest.objects.count()
        self.assertEqual(contest_num_before, contest_num_current)

    def test_04_invalid_form_02(self):
        # 4.user has permission but the form is invalid (start_time < end_time - freeze_time)
        # Expectation: failed to create a new contest
        target_url = reverse('contest:new')
        start_time = datetime.now()
        end_time = datetime.now() + timedelta(minutes=1)
        freeze_time = 60
        data = POST_data_of_editing_Contest(
            self.JUDGE_USER, start_time=start_time, end_time=end_time, freeze_time=freeze_time)
        contest_num_before = Contest.objects.count()
        response = self.JUDGE_CLIENT.post(target_url, data=data)
        contest_num_current = Contest.objects.count()
        self.assertEqual(contest_num_before, contest_num_current)

    def test_05_invalid_form_03(self):
        # 5.user has permission but the form is invalid (contest owner is not the same user)
        # Expectation: failed to create a new contest
        target_url = reverse('contest:new')
        data = POST_data_of_editing_Contest(self.ADMIN_USER)
        contest_num_before = Contest.objects.count()
        response = self.JUDGE_CLIENT.post(target_url, data=data)
        contest_num_current = Contest.objects.count()
        self.assertEqual(contest_num_before, contest_num_current)

    def test_06_create_contest(self):
        # 6.user has permission and the form is valid
        # Expectation: create a new contest successfully and redirect to view 'contest'
        target_url = reverse('contest:new')
        data = POST_data_of_editing_Contest(self.JUDGE_USER)
        response = self.JUDGE_CLIENT.post(target_url, data=data, follow=True)
        cid = Contest.objects.all().order_by("-pk")[0].pk
        redirect_url = reverse('contest:contest', args=[cid])
        self.assertRedirects(response, redirect_url)
        contest_obj = response.context['contest']
        self.assertEqual(contest_obj.owner, self.JUDGE_USER)
        self.assertEqual(contest_obj.cname, data['cname'])
        self.assertEqual(contest_obj.start_time.timetuple(), data['start_time'].timetuple())
        self.assertEqual(contest_obj.end_time.timetuple(), data['end_time'].timetuple())
