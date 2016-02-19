from django.test import TestCase, Client
from django.core.urlresolvers import reverse

from datetime import datetime, timedelta
from time import sleep

from users.forms import CodeSubmitForm
from utils.test_helper import *
from utils.file_info import get_extension


def preprocess(self):
    create_test_admin_user()
    # create 6 judge level users
    # (1 contest owner, 2 coowners,
    #  2 problem owners, 1 contestant)
    create_test_judge_user(6)
    create_test_normal_user()
    self.ADMIN_USER = get_test_admin_user()
    self.ADMIN_CLIENT = get_test_admin_client()
    self.JUDGE_USER = [get_test_judge_user(i) for i in range(6)]
    self.JUDGE_CLIENT = [get_test_judge_client(i) for i in range(6)]
    self.NORMAL_USER = get_test_normal_user()
    self.NORMAL_CLIENT = get_test_normal_user_client()
    self.ANONYMOUS_CLIENT = Client()
    self.CONTEST_OWNER = self.JUDGE_USER[0]
    self.CONTEST_COOWNERS = self.JUDGE_USER[1:3]
    self.CONTEST_PROBLEM_OWNERS = self.JUDGE_USER[3:5]
    self.CONTEST_CONTESTANTS = [self.JUDGE_USER[5], self.NORMAL_USER]
    self.CONTEST_PROBLEMS = []
    self.STATUSES = [
        Submission.ACCEPTED, Submission.NOT_ACCEPTED, Submission.COMPILE_ERROR,
        Submission.RESTRICTED_FUNCTION, Submission.JUDGE_ERROR, Submission.JUDGING]
    # create 2 problems for contest
    for i in range(2):
        problem = create_problem(
            self.CONTEST_PROBLEM_OWNERS[i], pname='contest_problem'+str(i),
            visible=True)
        self.CONTEST_PROBLEMS.append(problem)
    # create a running contest
    start_time = datetime.now() - timedelta(hours=1)
    end_time = datetime.now() + timedelta(hours=4)
    self.CONTEST = create_contest(
        self.CONTEST_OWNER, 'test_contest', start_time, end_time,
        self.CONTEST_COOWNERS, self.CONTEST_CONTESTANTS, self.CONTEST_PROBLEMS[0:2])

def all_submisions_when_contest_running(self):
    users = self.JUDGE_USER + [self.NORMAL_USER]
    submissions = []
    for problem in self.CONTEST_PROBLEMS:
        for user in users:
            for status in self.STATUSES:
                error_msg = random_word(50)
                submission = create_submission(
                    problem, user, status, error_msg=error_msg)
                submissions.append(submission)
    return submissions

def stop_running_contest(self):
    self.CONTEST.end_time = datetime.now()
    self.CONTEST.save()
    sleep(1)


class Tester_Status_error_message(TestCase):
    """ test view 'status:error_message' """

    def setUp(self):
        preprocess(self)

    def test_01_login(self):
        # 1.user does not login
        # Expectation: redirect to login page
        sid = 1
        target_url = reverse('status:error_message', args=[sid])
        redirect_url = reverse('users:login') + '?next=' + target_url
        response = self.ANONYMOUS_CLIENT.get(target_url)
        self.assertRedirects(response, redirect_url)

    def test_02_submission_not_found(self):
        # 2.submission does not exist
        # Expectation: error 404
        sid = 1000000
        target_url = reverse('status:error_message', args=[sid])
        response = self.NORMAL_CLIENT.get(target_url)
        self.assertEqual(response.status_code, 404)

    def test_03_permission_01(self):
        # 3.admin can see everyone's detail
        problem = self.CONTEST_PROBLEMS[0]
        users = [self.ADMIN_USER, self.JUDGE_USER[0], self.JUDGE_USER[1],
                 self.JUDGE_USER[3], self.JUDGE_USER[5], self.NORMAL_USER]
        for i in range(len(self.STATUSES)):
            error_msg = random_word(50)
            submission = create_submission(
                problem, users[i], self.STATUSES[i], error_msg=error_msg)
            target_url = reverse('status:error_message', args=[submission.pk])
            response = self.ADMIN_CLIENT.get(target_url)
            self.assertEqual(response.context['error_message'], error_msg)

    def test_04_permission_02(self):
        # 4.no one except admin can see admin's detail
        problem = self.CONTEST_PROBLEMS[0]
        user = self.ADMIN_USER
        for status in self.STATUSES:
            error_msg = random_word(50)
            submission = create_submission(
                problem, user, status, error_msg=error_msg)
            target_url = reverse('status:error_message', args=[submission.pk])
            response = self.JUDGE_CLIENT[0].get(target_url)
            self.assertEqual(response.status_code, 403)
            response = self.NORMAL_CLIENT.get(target_url)
            self.assertEqual(response.status_code, 403)

    def test_05_permission_03(self):
        # 5.during the contest running, the following rules are applied
        #   a) if the user is neither contest owner/coowner, nor admin,
        #      then this user cannot view anyone's detail
        #   b) owner / coowner of a contest cannot view detail submitted by
        #      the one who is not a contestant
        users = self.JUDGE_USER + [self.NORMAL_USER]
        clients = self.JUDGE_CLIENT + [self.NORMAL_CLIENT]
        contest_submissions = []
        for problem in self.CONTEST_PROBLEMS:
            for i, user in enumerate(users):
                for status in self.STATUSES:
                    error_msg = random_word(50)
                    submission = create_submission(
                        problem, user, status, error_msg=error_msg)
                    contest_submissions.append(submission)
                    for j, client in enumerate(clients):
                        target_url = reverse('status:error_message', args=[submission.pk])
                        response = client.get(target_url)
                        if j<3 and (i<3 or i>4):
                            self.assertEqual(response.context['error_message'], error_msg)
                        else:
                            self.assertEqual(response.status_code, 403)

    #the following tests should be run in normal mode (no contest is running)

    def test_06_permission_04(self):
        # 6.an user can view his own detail in normal mode
        users = self.JUDGE_USER + [self.NORMAL_USER]
        clients = self.JUDGE_CLIENT + [self.NORMAL_CLIENT]
        contest_submissions = all_submisions_when_contest_running(self)
        stop_running_contest(self)
        #submission during contest
        for i, _ in enumerate(self.CONTEST_PROBLEMS):
            for j, client in enumerate(clients):
                for k, _ in enumerate(self.STATUSES):
                    idx = i*42+j*6+k
                    error_msg = contest_submissions[idx].error_msg
                    target_url = reverse('status:error_message',
                                         args=[contest_submissions[idx].pk])
                    response = client.get(target_url)
                    self.assertEqual(response.context['error_message'], error_msg)
        #submission after contest
        for problem in self.CONTEST_PROBLEMS:
            for i, user in enumerate(users):
                for status in self.STATUSES:
                    error_msg = random_word(50)
                    submission = create_submission(
                        problem, user, status, error_msg=error_msg)
                    target_url = reverse('status:error_message', args=[submission.pk])
                    response = clients[i].get(target_url)
                    self.assertEqual(response.context['error_message'], error_msg)

    def test_07_permission_05(self):
        # 7.a problem owner can view detail of his/her problem in normal mode
        users = self.JUDGE_USER + [self.NORMAL_USER]
        clients = self.JUDGE_CLIENT[3:5]
        contest_submissions = all_submisions_when_contest_running(self)
        stop_running_contest(self)
        #submission during contest
        for i, _ in enumerate(self.CONTEST_PROBLEMS):
            for j, user in enumerate(users):
                for k, _ in enumerate(self.STATUSES):
                    idx = i*42+j*6+k
                    error_msg = contest_submissions[idx].error_msg
                    target_url = reverse('status:error_message',
                                         args=[contest_submissions[idx].pk])
                    response = clients[i].get(target_url)
                    self.assertEqual(response.context['error_message'], error_msg)
                    response = clients[1-i].get(target_url)
                    if j!=4-i:
                        self.assertEqual(response.status_code, 403)
        #submission after contest
        for i, problem in enumerate(self.CONTEST_PROBLEMS):
            for j, user in enumerate(users):
                for status in self.STATUSES:
                    error_msg = random_word(50)
                    submission = create_submission(
                        problem, user, status, error_msg=error_msg)
                    target_url = reverse('status:error_message', args=[submission.pk])
                    response = clients[i].get(target_url)
                    self.assertEqual(response.context['error_message'], error_msg)
                    response = clients[1-i].get(target_url)
                    if j!=4-i:
                        self.assertEqual(response.status_code, 403)

    def test_08_permission_06(self):
        # 8.in normal mode, contest owner/coowner can still view detail during the contest 
        users = self.JUDGE_USER + [self.NORMAL_USER]
        clients = self.JUDGE_CLIENT[0:3]
        contest_submissions = all_submisions_when_contest_running(self)
        stop_running_contest(self)
        # submission during contest (permission is the same as the moment contest was running)
        for i, _ in enumerate(self.CONTEST_PROBLEMS):
            for j, _ in enumerate(users):
                for k, _ in enumerate(self.STATUSES):
                    idx = i*42+j*6+k
                    error_msg = contest_submissions[idx].error_msg
                    target_url = reverse('status:error_message',
                                         args=[contest_submissions[idx].pk])
                    for client in clients:
                        response = client.get(target_url)
                        if j<3 or j>4:
                            self.assertEqual(response.context['error_message'], error_msg)
                        else:
                            self.assertEqual(response.status_code, 403)

        # submission after contest (no permission to view detail)
        for problem in self.CONTEST_PROBLEMS:
            for i, user in enumerate(users):
                for status in self.STATUSES:
                    error_msg = random_word(50)
                    submission = create_submission(
                        problem, user, status, error_msg=error_msg)
                    target_url = reverse('status:error_message', args=[submission.pk])
                    for j, client in enumerate(clients):
                        if j!=i:
                            response = client.get(target_url)
                            self.assertEqual(response.status_code, 403)


class Tester_Status_rejudge(TestCase):
    """ test view 'status:rejudge' """

    def setUp(self):
        preprocess(self)

    def test_01_login(self):
        # 1.user does not login
        # Expectation: redirect to login page
        sid = 1
        target_url = reverse('status:rejudge', args=[sid])
        redirect_url = reverse('users:login') + '?next=' + target_url
        response = self.ANONYMOUS_CLIENT.get(target_url)
        self.assertRedirects(response, redirect_url)

    def test_02_submission_not_found(self):
        # 2.submission does not exist
        # Expectation: error 404
        sid = 1000000
        target_url = reverse('status:rejudge', args=[sid])
        response = self.NORMAL_CLIENT.get(target_url)
        self.assertEqual(response.status_code, 404)

    def test_03_rejudge(self):
        # 3.only the one who meets one of the following conditions can rejudge:
        #   a) admin
        #   b) problem owner
        #   c) contest owner / coowner (can only rejudge the submissions during contest)
        users = [self.ADMIN_USER] + self.JUDGE_USER + [self.NORMAL_USER]
        clients = [self.ADMIN_CLIENT] + self.JUDGE_CLIENT + [self.NORMAL_CLIENT]
        contest_submissions = []
        #rejudge when the contest is running
        for i, problem in enumerate(self.CONTEST_PROBLEMS):
            for user in users:
                for status in self.STATUSES:
                    submission = create_submission(problem, user, status)
                    contest_submissions.append(submission)
                    for j, client in enumerate(clients):
                        target_url = reverse('status:rejudge', args=[submission.pk])
                        response = client.get(target_url)
                        if j<4 or j==i+4:
                            rejudged = Submission.objects.get(pk=submission.pk)
                            self.assertEqual(rejudged.status, Submission.WAIT)
                            rejudged.status = status
                            rejudged.save()
                        else:
                            self.assertEqual(response.status_code, 403)
        #stop running contest such that there is no contest running
        stop_running_contest(self)
        #rejudge submissions submitted during contest
        for i, _ in enumerate(self.CONTEST_PROBLEMS):
            for j, _ in enumerate(users):
                for k, _ in enumerate(self.STATUSES):
                    target_url = reverse(
                        'status:rejudge',
                        args=[contest_submissions[i*48+j*6+k].pk])
                    for p, client in enumerate(clients):
                        response = client.get(target_url)
                        if p<4 or p==i+4:
                            rejudged = Submission.objects.get(
                                pk=contest_submissions[i*48+j*6+k].pk)
                            self.assertEqual(rejudged.status, Submission.WAIT)
                        else:
                            self.assertEqual(response.status_code, 403)
        #rejudge the submissions submitted after contest
        for problem in self.CONTEST_PROBLEMS:
            for user in users:
                for status in self.STATUSES:
                    submission = create_submission(problem, user, status)
                    for i, client in enumerate(clients):
                        target_url = reverse('status:rejudge', args=[submission.pk])
                        response = client.get(target_url)
                        if i in [0, 4, 5]:
                            rejudged = Submission.objects.get(pk=submission.pk)
                            self.assertEqual(rejudged.status, Submission.WAIT)
                        else:
                            self.assertEqual(response.status_code, 403)


class Tester_Status_view_code(TestCase):
    """ test view 'status:view_code' """

    def setUp(self):
        create_test_directory()
        preprocess(self)

    def tearDown(self):
        remove_test_directory()

    def test_01_login(self):
        """ test view 'view_code' """
        # 1.user does not login
        # Expectation: redirect to login page
        sid = 1
        target_url = reverse('status:view_code', args=[sid])
        redirect_url = reverse('users:login') + '?next=' + target_url
        response = self.ANONYMOUS_CLIENT.get(target_url)
        self.assertRedirects(response, redirect_url)

    def test_02_submission_not_found(self):
        # 2.submission does not exist
        # Expectation: error 404
        sid = 1000000
        target_url = reverse('status:view_code', args=[sid])
        response = self.NORMAL_CLIENT.get(target_url)
        self.assertEqual(response.status_code, 404)

    def test_03_file_not_found(self):
        # 3.code file related to the submission does not exist
        # Expectation: error 404
        submission = create_submission(
                        self.CONTEST_PROBLEMS[0], self.ADMIN_USER, self.STATUSES[0])
        target_url = reverse('status:view_code', args=[submission.pk])
        response = self.ADMIN_CLIENT.get(target_url)
        filename = '%s.%s' % (submission.pk, get_extension(submission.language))
        self.assertEqual(response.status_code, 404)

    def test_04_permission_01(self):
        # 4.admin can see everyone's detail
        problem = self.CONTEST_PROBLEMS[0]
        users = [self.ADMIN_USER, self.JUDGE_USER[0], self.JUDGE_USER[1],
                 self.JUDGE_USER[3], self.JUDGE_USER[5], self.NORMAL_USER]
        for i in range(len(self.STATUSES)):
            submission = create_submission(
                problem, users[i], self.STATUSES[i])
            file_name, code = create_source_code(
                CodeSubmitForm.SUBMIT_PATH, submission.pk,
                get_extension(submission.language))
            target_url = reverse('status:view_code', args=[submission.pk])
            response = self.ADMIN_CLIENT.get(target_url)
            remove_file_if_exists(file_name)
            self.assertContains(response, code)

    def test_05_permission_02(self):
        # 5.no one except admin can see admin's detail
        problem = self.CONTEST_PROBLEMS[0]
        user = self.ADMIN_USER
        for status in self.STATUSES:
            submission = create_submission(problem, user, status)
            target_url = reverse('status:view_code', args=[submission.pk])
            response = self.JUDGE_CLIENT[0].get(target_url)
            self.assertEqual(response.status_code, 403)
            response = self.NORMAL_CLIENT.get(target_url)
            self.assertEqual(response.status_code, 403)

    def test_06_permission_03(self):
        # 6.during the contest, only owner/coowner can view contestants' detail
        users = self.JUDGE_USER + [self.NORMAL_USER]
        clients = self.JUDGE_CLIENT + [self.NORMAL_CLIENT]
        contest_submissions = []
        for problem in self.CONTEST_PROBLEMS:
            for i, user in enumerate(users):
                for status in self.STATUSES:
                    submission = create_submission(problem, user, status)
                    contest_submissions.append(submission)
                    for j, client in enumerate(clients):
                        file_name, code = create_source_code(
                            CodeSubmitForm.SUBMIT_PATH, submission.pk,
                            get_extension(submission.language))
                        target_url = reverse('status:view_code', args=[submission.pk])
                        response = client.get(target_url)
                        remove_file_if_exists(file_name)
                        if j<3 and (i<3 or i>4):
                            self.assertContains(response, code)
                        else:
                            self.assertEqual(response.status_code, 403)

    #the following tests should under the condition that no contest is running

    def test_07_permission_04(self):
        # 7.a user can view his own detail in normal mode
        users = self.JUDGE_USER + [self.NORMAL_USER]
        clients = self.JUDGE_CLIENT + [self.NORMAL_CLIENT]
        contest_submissions = all_submisions_when_contest_running(self)
        stop_running_contest(self)
        #submission during contest
        for i, _ in enumerate(self.CONTEST_PROBLEMS):
            for j, client in enumerate(clients):
                for k, _ in enumerate(self.STATUSES):
                    idx = i*42+j*6+k
                    file_name, code = create_source_code(
                        CodeSubmitForm.SUBMIT_PATH, contest_submissions[idx].pk,
                        get_extension(contest_submissions[idx].language))
                    target_url = reverse('status:view_code',
                                         args=[contest_submissions[idx].pk])
                    response = client.get(target_url)
                    remove_file_if_exists(file_name)
                    self.assertContains(response, code)
        #submission after contest
        for problem in self.CONTEST_PROBLEMS:
            for i, user in enumerate(users):
                for status in self.STATUSES:
                    submission = create_submission(problem, user, status)
                    file_name, code = create_source_code(
                        CodeSubmitForm.SUBMIT_PATH, submission.pk,
                        get_extension(submission.language))
                    target_url = reverse('status:view_code', args=[submission.pk])
                    response = clients[i].get(target_url)
                    remove_file_if_exists(file_name)
                    self.assertContains(response, code)

    def test_08_permission_05(self):
        # 8.a problem owner can view detail of his/her problem in normal mode
        users = self.JUDGE_USER + [self.NORMAL_USER]
        clients = self.JUDGE_CLIENT[3:5]
        contest_submissions = all_submisions_when_contest_running(self)
        stop_running_contest(self)
        #submission during contest
        for i, _ in enumerate(self.CONTEST_PROBLEMS):
            for j, _ in enumerate(users):
                for k, _ in enumerate(self.STATUSES):
                    idx = i*42+j*6+k
                    file_name, code = create_source_code(
                        CodeSubmitForm.SUBMIT_PATH, contest_submissions[idx].pk,
                        get_extension(contest_submissions[idx].language))
                    target_url = reverse('status:view_code',
                                         args=[contest_submissions[idx].pk])
                    response = clients[i].get(target_url)
                    response2 = clients[1-i].get(target_url)
                    remove_file_if_exists(file_name)
                    self.assertContains(response, code)
                    if j!=4-i:
                        self.assertEqual(response2.status_code, 403)
        #submission after contest
        for i, problem in enumerate(self.CONTEST_PROBLEMS):
            for j, user in enumerate(users):
                for status in self.STATUSES:
                    submission = create_submission(problem, user, status)
                    file_name, code = create_source_code(
                        CodeSubmitForm.SUBMIT_PATH, submission.pk,
                        get_extension(submission.language))
                    target_url = reverse('status:view_code', args=[submission.pk])
                    response = clients[i].get(target_url)
                    response2 = clients[1-i].get(target_url)
                    remove_file_if_exists(file_name)
                    self.assertContains(response, code)
                    if j!=4-i:
                        self.assertEqual(response2.status_code, 403)

    def test_09_permission_06(self):
        # 9.in normal mode, contest owner/coowner can still view detail during the contest
        users = self.JUDGE_USER + [self.NORMAL_USER]
        clients = self.JUDGE_CLIENT[0:3]
        contest_submissions = all_submisions_when_contest_running(self)
        stop_running_contest(self)
        #submission during contest (permission is the same as the moment contest was running)
        for i, _ in enumerate(self.CONTEST_PROBLEMS):
            for j, _ in enumerate(users):
                for k, _ in enumerate(self.STATUSES):
                    idx = i*42+j*6+k
                    target_url = reverse('status:view_code',
                                         args=[contest_submissions[idx].pk])
                    for client in clients:
                        file_name, code = create_source_code(
                            CodeSubmitForm.SUBMIT_PATH, contest_submissions[idx].pk,
                            get_extension(contest_submissions[idx].language))
                        response = client.get(target_url)
                        remove_file_if_exists(file_name)
                        if j<3 or j>4:
                            self.assertContains(response, code)
                        else:
                            self.assertEqual(response.status_code, 403)
        # submission after contest (no permission to view detail)
        for problem in self.CONTEST_PROBLEMS:
            for j, user in enumerate(users):
                for status in self.STATUSES:
                    submission = create_submission(problem, user, status)
                    target_url = reverse('status:view_code', args=[submission.pk])
                    for p, client in enumerate(clients):
                        if p!=j:
                            response = client.get(target_url)
                            self.assertEqual(response.status_code, 403)
