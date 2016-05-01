from django.test import TestCase, Client
from django.core.urlresolvers import reverse

from datetime import datetime, timedelta

from contest.models import Contest
from utils.nthuoj_testcase import NTHUOJ_TestCase_Basic
from utils.nthuoj_testcase import NTHUOJ_TestCase_Complex01, NTHUOJ_TestCase_Complex02
from utils.test_helper import *


class Tester_Contest_new(NTHUOJ_TestCase_Basic):
    """ test view 'contest:new' """

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


class Tester_Contest_delete(TestCase):
    """ test view 'contest:delete' """

    def setUp(self):
        create_test_admin_user()
        create_test_judge_user(3)
        create_test_normal_user()
        self.ADMIN_USER = get_test_admin_user()
        self.ADMIN_CLIENT = get_test_admin_client()
        self.JUDGE_USERS = [get_test_judge_user(i) for i in xrange(3)]
        self.JUDGE_CLIENTS = [get_test_judge_client(i) for i in xrange(3)]
        self.NORMAL_USER = get_test_normal_user()
        self.NORMAL_CLIENT = get_test_normal_user_client()
        self.ANONYMOUS_CLIENT = Client()

    def test_01_login(self):
        # 1.user does not login
        # Expectation: redirect to login page
        cid = 1
        target_url = reverse('contest:delete', args=[cid])
        redirect_url = reverse('users:login') + '?next=' + target_url
        response = self.ANONYMOUS_CLIENT.get(target_url)
        self.assertRedirects(response, redirect_url)

    def test_02_contest_not_found(self):
        # 2.contest does not exist
        # Expectation: error 404
        cid = 1000000
        target_url = reverse('contest:delete', args=[cid])
        response = self.JUDGE_CLIENTS[0].get(target_url)
        self.assertEqual(response.status_code, 404)

    def test_03_permission(self):
        # 3.user has no permission (only admin or contest owner can delete)
        # Expectation: error 403
        owner = self.JUDGE_USERS[0]
        coowners = self.JUDGE_USERS[1:3]
        new_contest = create_contest(owner, coowners=coowners)
        target_url = reverse('contest:delete', args=[new_contest.pk])
        contest_num_before = Contest.objects.count()
        for i in range(1,3):
            response = self.JUDGE_CLIENTS[i].get(target_url)
            contest_num_current = Contest.objects.count()
            self.assertEqual(response.status_code, 403)
            self.assertEqual(contest_num_before, contest_num_before)
        response = self.NORMAL_CLIENT.get(target_url)
        contest_num_current = Contest.objects.count()
        self.assertEqual(response.status_code, 403)
        self.assertEqual(contest_num_before, contest_num_before)

    def test_04_delete_contest(self):
        # 4.user has permission
        # Expectation: delete the contest successfully and redirect to view 'archive'
        owner = self.JUDGE_USERS[0]
        coowners = self.JUDGE_USERS[1:3]
        clients = [self.ADMIN_CLIENT, self.JUDGE_CLIENTS[0]]
        for client in clients:
            new_contest = create_contest(owner, coowners=coowners)
            target_url = reverse('contest:delete', args=[new_contest.pk])
            redirect_url = reverse('contest:archive')
            response = client.get(target_url)
            try:
                result = False
                contest = Contest.objects.get(id=new_contest.pk)
            except Contest.DoesNotExist:
                result = True
            self.assertRedirects(response, redirect_url)
            self.assertTrue(result)


class Tester_Contest_contest_info(NTHUOJ_TestCase_Complex02):
    """ test view 'contest:contest_info' """

    def test_01_contest_info(self):
        target_url = reverse('contest:contest_info', args=[self.CONTEST.pk])
        response = self.NORMAL_CLIENTS[0].get(target_url)
        self.assertEqual(response.context['contest'], self.CONTEST)
        response = self.JUDGE_CLIENTS[0].get(target_url)
        self.assertEqual(response.context['contest'], self.CONTEST)
        response = self.ADMIN_CLIENT.get(target_url)
        self.assertEqual(response.context['contest'], self.CONTEST)


class Tester_Contest_edit(NTHUOJ_TestCase_Complex01):
    """ test view 'contest:edit' """

    def test_01_login(self):
        # 1.user does not login
        # Expectation: redirect to login page
        cid = 1
        target_url = reverse('contest:edit', args=[cid])
        redirect_url = reverse('users:login') + '?next=' + target_url
        response = self.ANONYMOUS_CLIENT.get(target_url)
        self.assertRedirects(response, redirect_url)

    def test_02_contest_not_found(self):
        # 2.contest does not exist
        # Expectation: error 404
        cid = 1000000
        target_url = reverse('contest:edit', args=[cid])
        response = self.JUDGE_CLIENTS[0].get(target_url)
        self.assertEqual(response.status_code, 404)

    def test_03_permission(self):
        # 3.user has no permission (only admin and contest owner/coowner can edit)
        # Expectation: error 403
        data = POST_data_of_editing_Contest(
            self.CONTEST_OWNER, coowners=self.CONTEST_COOWNERS, problems=self.CONTEST_PROBLEMS)
        new_contest = create_contest_by_data(data)
        target_url = reverse('contest:edit', args=[new_contest.pk])
        data['cname'] = random_word(20)
        clients = self.JUDGE_CLIENTS[3:5] + [self.NORMAL_CLIENT]
        for client in clients:
            response = client.get(target_url)
            self.assertEqual(response.status_code, 403)
            response = client.post(target_url, data=data)
            self.assertEqual(response.status_code, 403)
        contest_obj = Contest.objects.get(pk=new_contest.pk)
        self.assertEqual(contest_obj, new_contest)

    def test_04_invalid_form_01(self):
        # 4.user has permission but form is invalid (start_time < end_time)
        # Expectation: failed to edit the contest
        data = POST_data_of_editing_Contest(
            self.CONTEST_OWNER, coowners=self.CONTEST_COOWNERS, problems=self.CONTEST_PROBLEMS)
        new_contest = create_contest_by_data(data)
        target_url = reverse('contest:edit', args=[new_contest.pk])
        data['start_time'] = datetime.now()
        data['end_time'] = datetime.now() + timedelta(days=-1)
        clients = self.JUDGE_CLIENTS[0:3] + [self.ADMIN_CLIENT]
        for client in clients:
            response = client.post(target_url, data=data)
            self.assertEqual(response.context['contest'], new_contest)
            self.assertContains(response, "Some fields are invalid!")

    def test_05_invalid_form_02(self):
        # 5.user has permission but form is invalid (start_time < end_time - freeze_time)
        # Expectation: failed to edit the contest
        data = POST_data_of_editing_Contest(
            self.CONTEST_OWNER, coowners=self.CONTEST_COOWNERS, problems=self.CONTEST_PROBLEMS)
        new_contest = create_contest_by_data(data)
        target_url = reverse('contest:edit', args=[new_contest.pk])
        data['start_time'] = datetime.now()
        data['end_time'] = datetime.now() + timedelta(minutes=1)
        data['freeze_time'] = 60
        clients = self.JUDGE_CLIENTS[0:3] + [self.ADMIN_CLIENT]
        for client in clients:
            response = client.post(target_url, data=data)
            self.assertEqual(response.context['contest'], new_contest)
            self.assertContains(response, "Some fields are invalid!")

    def test_06_invalid_form_03(self):
        # 6.user has permission but form is invalid (contest owner is not the same user)
        # Expectation: failed to edit the contest
        data = POST_data_of_editing_Contest(
            self.CONTEST_OWNER, coowners=self.CONTEST_COOWNERS, problems=self.CONTEST_PROBLEMS)
        new_contest = create_contest_by_data(data)
        target_url = reverse('contest:edit', args=[new_contest.pk])
        data['owner'] = self.JUDGE_USERS[3].username
        clients = self.JUDGE_CLIENTS[0:3] + [self.ADMIN_CLIENT]
        for client in self.JUDGE_CLIENTS[0:3]:
            response = client.post(target_url, data=data)
            self.assertEqual(response.context['contest'], new_contest)
            self.assertContains(response, "Some fields are invalid!")

    def test_07_edit_contest(self):
        # 7.user has permission and the form is valid
        # Expectation: edit the contest successfully and redirect to view 'contest'
        data = POST_data_of_editing_Contest(
            self.CONTEST_OWNER, coowners=self.CONTEST_COOWNERS, problems=self.CONTEST_PROBLEMS)
        new_contest = create_contest_by_data(data)
        target_url = reverse('contest:edit', args=[new_contest.pk])
        redirect_url = reverse('contest:contest', args=[new_contest.pk])
        data['cname'] = random_word(20)
        data['start_time'] = datetime.now() + timedelta(hours=-2)
        data['end_time'] = datetime.now() + timedelta(hours=3)
        data['freeze_time'] = 100
        edited_problems = [self.CONTEST_PROBLEMS[1]]
        data['problem'] = tuple([problem.pk for problem in edited_problems])
        edited_coowners = [self.CONTEST_COOWNERS[1]]
        data['coowner'] = tuple([user.username for user in edited_coowners])
        response = self.JUDGE_CLIENTS[0].post(target_url, data=data, follow=True)
        self.assertRedirects(response, redirect_url)
        edited_contest = Contest.objects.get(pk=new_contest.pk)
        self.assertEqual(edited_contest.cname, data['cname'])
        self.assertEqual(edited_contest.start_time.timetuple(), data['start_time'].timetuple())
        self.assertEqual(edited_contest.end_time.timetuple(), data['end_time'].timetuple())
        self.assertEqual(edited_contest.freeze_time, data['freeze_time'])
        current_contest_problems = [problem.pk for problem in edited_contest.problem.all()]
        self.assertEqual(tuple(current_contest_problems), data['problem'])
        current_contest_coowners = [user.username for user in edited_contest.coowner.all()]
        self.assertEqual(tuple(current_contest_coowners), data['coowner'])
