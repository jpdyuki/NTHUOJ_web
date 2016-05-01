from django.core.urlresolvers import reverse

from contest.models import Contest, Clarification
from utils.nthuoj_testcase import NTHUOJ_TestCase_Complex02
from utils.test_helper import *


class Tester_Contest_ask(NTHUOJ_TestCase_Complex02):
    """ test view 'contest:ask' """

    def test_01_login(self):
        # 1.user does not login
        # Expectation: redirect to login page
        target_url = reverse('contest:ask')
        redirect_url = reverse('users:login') + '?next=' + target_url
        response = self.ANONYMOUS_CLIENT.post(target_url)
        self.assertRedirects(response, redirect_url)

    def test_02_contest_not_found(self):
        # 2.contest does not exist
        # Expectation: error 404
        cid = 1000000
        pid = self.CONTEST_PROBLEMS[0].pk
        asker = self.JUDGE_USERS[0].username
        content = random_word(100)
        target_url = reverse('contest:ask')
        data = {
            'contest': cid,
            'problem': pid,
            'asker': asker,
            'content': content,
        }
        response = self.JUDGE_CLIENTS[0].post(target_url, data=data)
        self.assertEqual(response.status_code, 404)

    def test_03_permission(self):
        # 3.user has no permission (only admin and contest owner/coowner/contestant can ask)
        # Expectation: failed to create a clarification and redirect to view 'contest'
        cid = self.CONTEST.pk
        pid = self.CONTEST_PROBLEMS[0].pk
        askers = self.JUDGE_USERS[3:5] + [self.NORMAL_USERS[50]]
        clients = self.JUDGE_CLIENTS[3:5] + [self.NORMAL_CLIENTS[50]]
        content = random_word(100)
        target_url = reverse('contest:ask')
        redirect_url = reverse('contest:contest', args=[cid])
        clarification_num_before = Clarification.objects.count()
        for i in range(3):
            data = {
                'contest': cid,
                'problem': pid,
                'asker': askers[i].username,
                'content': content,
            }
            response = clients[i].post(target_url, data=data, follow=True)
            clarification_num_current = Clarification.objects.count()
            self.assertRedirects(response, redirect_url)
            self.assertEqual(clarification_num_before, clarification_num_current)

    def test_04_invalid_form(self):
        # 4.user has permission but form is invalid (problem is not in the contest)
        # Expectation: failed to create a clarification and redirect to view 'contest'
        cid = self.CONTEST.pk
        pid = 1000000
        askers = [self.ADMIN_USER] + self.JUDGE_USERS[0:3] + self.NORMAL_USERS[0:50]
        clients = [self.ADMIN_CLIENT] + self.JUDGE_CLIENTS[0:3] + self.NORMAL_CLIENTS[0:50]
        target_url = reverse('contest:ask')
        redirect_url = reverse('contest:contest', args=[cid])
        clarification_num_before = Clarification.objects.count()
        for i in range(53):
            content = random_word(100)
            data = {
                'contest': cid,
                'problem': pid,
                'asker': askers[i].username,
                'content': content,
            }
            response = clients[i].post(target_url, data=data, follow=True)
            clarification_num_current = Clarification.objects.count()
            self.assertRedirects(response, redirect_url)
            self.assertEqual(clarification_num_before, clarification_num_current)

    def test_05_ask(self):
        # 5.user has permission and form is valid
        # Expectation: create a new clarification successfully and redirect to view 'contest'
        cid = self.CONTEST.pk
        pid = self.CONTEST_PROBLEMS[0].pk
        askers = [self.ADMIN_USER] + self.JUDGE_USERS[0:3] + self.NORMAL_USERS[0:50]
        clients = [self.ADMIN_CLIENT] + self.JUDGE_CLIENTS[0:3] + self.NORMAL_CLIENTS[0:50]
        target_url = reverse('contest:ask')
        redirect_url = reverse('contest:contest', args=[cid])
        for i in range(53):
            content = random_word(100)
            data = {
                'contest': cid,
                'problem': pid,
                'asker': askers[i].username,
                'content': content,
            }
            response = clients[i].post(target_url, data=data, follow=True)
            self.assertRedirects(response, redirect_url)
            clarification = Clarification.objects.all().order_by("-pk")[0]
            self.assertEqual(clarification.content, content)
            self.assertEqual(clarification.contest, self.CONTEST)
            self.assertEqual(clarification.problem, self.CONTEST_PROBLEMS[0])


class Tester_Contest_reply(NTHUOJ_TestCase_Complex02):
    """ test view 'contest:reply' """

    def test_01_login(self):
        # 1.user does not login
        # Expectation: redirect to login page
        target_url = reverse('contest:reply')
        redirect_url = reverse('users:login') + '?next=' + target_url
        response = self.ANONYMOUS_CLIENT.post(target_url)
        self.assertRedirects(response, redirect_url)

    def test_02_clarification_not_found(self):
        # 2.clarification does not exist
        # Expectation: error 404
        clid = 10000
        replier = self.JUDGE_USERS[0].username
        reply = random_word(100)
        reply_all = False
        target_url = reverse('contest:reply')
        data = {
            'clarification': clid,
            'replier': replier,
            'reply': reply,
            'reply_all': reply_all,
        }
        response = self.JUDGE_CLIENTS[0].post(target_url, data=data)
        self.assertEqual(response.status_code, 404)

    def test_03_permission(self):
        # 3.user has no permission (only admin and contest owner/coowner can reply)
        # Expectation: failed to reply to a clarification request and redirect to view 'archive'
        contest = self.CONTEST
        problem = self.CONTEST_PROBLEMS[0]
        asker = self.NORMAL_USERS[0]
        clarification = create_clarification(contest, problem, asker)
        clid = clarification.pk
        repliers = self.JUDGE_USERS[3:6] + self.NORMAL_USERS[0:51]
        clients = self.JUDGE_CLIENTS[3:6] + self.NORMAL_CLIENTS[0:51]
        reply = random_word(100)
        reply_all = False
        target_url = reverse('contest:reply')
        redirect_url = reverse('contest:archive')
        for i in range(54):
            data = {
                'clarification': clid,
                'replier': repliers[i].username,
                'reply': reply,
                'reply_all': reply_all,
            }
            response = clients[i].post(target_url, data=data, follow=True)
            self.assertRedirects(response, redirect_url)
            clarification_current = Clarification.objects.get(pk=clid)
            self.assertEqual(clarification, clarification_current)

    def test_04_reply(self):
        # 4.user has permission and form is valid
        # Expectation: create a new clarification successfully and redirect to view 'contest'
        contest = self.CONTEST
        problem = self.CONTEST_PROBLEMS[0]
        asker = self.NORMAL_USERS[0]
        clarification = create_clarification(contest, problem, asker)
        clid = clarification.pk
        repliers = [self.ADMIN_USER] + self.JUDGE_USERS[0:3]
        clients = [self.ADMIN_CLIENT] + self.JUDGE_CLIENTS[0:3]
        reply_all = False
        target_url = reverse('contest:reply')
        redirect_url = reverse('contest:contest', args=[contest.pk])
        for i in range(4):
            reply = random_word(100)
            data = {
                'clarification': clid,
                'replier': repliers[i].username,
                'reply': reply,
                'reply_all': reply_all,
            }
            response = clients[i].post(target_url, data=data, follow=True)
            self.assertRedirects(response, redirect_url)
            clarification_current = Clarification.objects.get(pk=clid)
            self.assertEqual(clarification_current.replier, repliers[i])
            self.assertEqual(clarification_current.reply, reply)
            self.assertEqual(clarification_current.reply_all, reply_all)
