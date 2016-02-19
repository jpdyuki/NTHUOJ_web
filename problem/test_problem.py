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


class Tester_Problem_delete_problem(TestCase):
    """ test view 'problem:delete_problem' """

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
        target_url = reverse('problem:delete_problem', args=[pid])
        redirect_url = reverse('users:login') + '?next=' + target_url
        response = self.ANONYMOUS_CLIENT.get(target_url)
        self.assertRedirects(response, redirect_url)

    def test_02_problem_not_found(self):
        # 2.problem does not exist
        # Expectation: error 404
        pid = 1000000
        target_url = reverse('problem:delete_problem', args=[pid])
        response = self.ADMIN_CLIENT.get(target_url)
        self.assertEqual(response.status_code, 404)

    def test_03_permission(self):
        # 3.user has no permission
        # Expectation: error 403
        problem = create_problem(self.ADMIN_USER)
        target_url = reverse('problem:delete_problem', args=[problem.pk])
        response = self.JUDGE_CLIENT.get(target_url)
        self.assertEqual(response.status_code, 403)

    def test_04_delete_problem(self):
        # 4.problem exists and user has permission
        # Expectation: delete the problem successfully and redirect to view 'problem'
        problem = create_problem(self.ADMIN_USER)
        target_url = reverse('problem:delete_problem', args=[problem.pk])
        redirect_url = reverse('problem:problem')
        response = self.ADMIN_CLIENT.get(target_url)
        self.assertRedirects(response, redirect_url)
        response = self.ADMIN_CLIENT.get(target_url)
        self.assertEqual(response.status_code, 404)


class Tester_Problem_edit(TestCase):
    """ test view 'problem:edit' """

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
        target_url = reverse('problem:edit', args=[pid])
        redirect_url = reverse('users:login') + '?next=' + target_url
        response = self.ANONYMOUS_CLIENT.get(target_url)
        self.assertRedirects(response, redirect_url)

    def test_02_problem_not_found(self):
        # 2.problem does not exist
        # Expectation: error 404
        pid = 1000000
        target_url = reverse('problem:edit', args=[pid])
        response = self.ADMIN_CLIENT.get(target_url)
        self.assertEqual(response.status_code, 404)

    def test_03_permission(self):
        # 3.user has no permission
        # Expectation: error 403
        problem = create_problem(self.JUDGE_USER)
        target_url = reverse('problem:edit', args=[problem.pk])
        response = self.NORMAL_CLIENT.get(target_url)
        self.assertEqual(response.status_code, 403)

    def test_04_edit_property(self):
        # 4.using POST method with arguments 'description', 'input', 'output',
        #   'sample_in', 'sample_out', 'visible', 'judge_source', 'judge_type',
        #   and 'judge_language'
        # Expectation: edit problem with respect to those arguments, and redirect to view 'detail'
        problem = create_problem(self.JUDGE_USER)
        target_url = reverse('problem:edit', args=[problem.pk])
        data = POST_data_of_editing_Problem(self.JUDGE_USER)
        response = self.JUDGE_CLIENT.post(target_url, data=data, follow=True)
        redirect_url = reverse('problem:detail', args=[problem.pk])
        self.assertRedirects(response, redirect_url)
        edited_problem = response.context['problem']
        self.assertEqual(edited_problem.description, data['description'])
        self.assertEqual(edited_problem.input, data['input'])
        self.assertEqual(edited_problem.output, data['output'])
        self.assertEqual(edited_problem.sample_in, data['sample_in'])
        self.assertEqual(edited_problem.sample_out, data['sample_out'])
        self.assertEqual(edited_problem.visible, data['visible'])
        self.assertEqual(edited_problem.judge_source, data['judge_source'])
        self.assertEqual(edited_problem.judge_type, data['judge_type'])
        self.assertEqual(edited_problem.judge_language, data['judge_language'])

    def test_05_upload_special_judge_code(self):
        # 5.using POST method with argument 'special_judge_code'
        # Expectation: upload special judge code to server successfully
        problem = create_problem(self.JUDGE_USER)
        target_url = reverse('problem:edit', args=[problem.pk])
        data = POST_data_of_editing_Problem(self.JUDGE_USER, judge_type=Problem.SPECIAL)
        file_ex = get_problem_file_extension(problem)
        special_judge_code = create_judge_code('special', problem.pk, file_ex)
        try:
            with open(special_judge_code, 'r') as fp:
                data['special_judge_code'] = fp
                response = self.JUDGE_CLIENT.post(target_url, data=data, follow=True)
        except (IOError, OSError):
            print "Something went wrong when reading special judge files for testing..."
        uploaded_special_judge_code = '%s%s%s' % (SPECIAL_PATH, problem.pk, file_ex)
        compare_result = compare_local_and_uploaded_file(
            special_judge_code, uploaded_special_judge_code)
        remove_file_if_exists(special_judge_code)
        remove_file_if_exists(uploaded_special_judge_code)
        self.assertTrue(compare_result)

    def test_06_upload_partial_judge_code_and_header(self):
        # 6.using POST method with argument 'partial_judge_code' and 'partial_judge_header'
        # Expectation: upload partial judge code and header to server successfully
        problem = create_problem(self.JUDGE_USER)
        target_url = reverse('problem:edit', args=[problem.pk])
        data = POST_data_of_editing_Problem(self.JUDGE_USER, judge_type=Problem.PARTIAL)
        file_ex = get_problem_file_extension(problem)
        partial_judge_code = create_judge_code('partial', problem.pk, file_ex)
        partial_judge_header = create_judge_code('partial', problem.pk, '.h')
        try:
            with open(partial_judge_code, 'r') as fp, open(partial_judge_header, 'r') as fp2:
                data['partial_judge_code'] = fp
                data['partial_judge_header'] = fp2
                response = self.JUDGE_CLIENT.post(target_url, data=data, follow=True)
        except (IOError, OSError):
            print "Something went wrong when reading partial judge files for testing..."
        uploaded_partial_judge_code = '%s%s%s' % (PARTIAL_PATH, problem.pk, file_ex)
        uploaded_partial_judge_header = '%s%s.h' % (PARTIAL_PATH, problem.pk)
        compare_result = compare_local_and_uploaded_file(
            partial_judge_code, uploaded_partial_judge_code)
        compare_result2 = compare_local_and_uploaded_file(
            partial_judge_header, uploaded_partial_judge_header)
        remove_file_if_exists(partial_judge_code)
        remove_file_if_exists(uploaded_partial_judge_code)
        remove_file_if_exists(partial_judge_header)
        remove_file_if_exists(uploaded_partial_judge_header)
        self.assertTrue(compare_result and compare_result2)

    def test_07_change_judge_type_01(self):
        # 7.changing judge type from special judge to partial judge
        # Expectation: remove all special judge files with respect to this problem
        problem = create_problem(self.JUDGE_USER)
        target_url = reverse('problem:edit', args=[problem.pk])
        data = POST_data_of_editing_Problem(self.JUDGE_USER, judge_type=Problem.SPECIAL)
        file_ex = get_problem_file_extension(problem)
        special_judge_code = create_judge_code('special', problem.pk, file_ex)
        try:
            with open(special_judge_code, 'r') as fp:
                data['special_judge_code'] = fp
                response = self.JUDGE_CLIENT.post(target_url, data=data, follow=True)
        except (IOError, OSError):
            print "Something went wrong when reading special judge files for testing..."
        data = POST_data_of_editing_Problem(self.JUDGE_USER, judge_type=Problem.PARTIAL)
        partial_judge_code = create_judge_code('partial', problem.pk, file_ex)
        partial_judge_header = create_judge_code('partial', problem.pk, '.h')
        try:
            with open(partial_judge_code, 'r') as fp, open(partial_judge_header, 'r') as fp2:
                data['partial_judge_code'] = fp
                data['partial_judge_header'] = fp2
                response = self.JUDGE_CLIENT.post(target_url, data=data, follow=True)
        except (IOError, OSError):
            print "Something went wrong when reading partial judge files for testing..."
        uploaded_special_judge_code = '%s%s%s' % (SPECIAL_PATH, problem.pk, file_ex)
        uploaded_partial_judge_code = '%s%s%s' % (PARTIAL_PATH, problem.pk, file_ex)
        uploaded_partial_judge_header = '%s%s.h' % (PARTIAL_PATH, problem.pk)
        result = os.path.isfile(uploaded_special_judge_code)
        result2 = os.path.isfile(uploaded_partial_judge_code)
        result3 = os.path.isfile(uploaded_partial_judge_header)
        remove_file_if_exists(special_judge_code)
        remove_file_if_exists(uploaded_special_judge_code)
        remove_file_if_exists(partial_judge_code)
        remove_file_if_exists(uploaded_partial_judge_code)
        remove_file_if_exists(partial_judge_header)
        remove_file_if_exists(uploaded_partial_judge_header)
        self.assertFalse(result)
        self.assertTrue(result2)
        self.assertTrue(result3)

    def test_08_change_judge_type_02(self):       
        # 8.changing judge type from partial judge to special judge
        # Expectation: remove all partial judge files with respect to this problem
        problem = create_problem(self.JUDGE_USER)
        target_url = reverse('problem:edit', args=[problem.pk])
        data = POST_data_of_editing_Problem(self.JUDGE_USER, judge_type=Problem.PARTIAL)
        file_ex = get_problem_file_extension(problem)
        partial_judge_code = create_judge_code('partial', problem.pk, file_ex)
        partial_judge_header = create_judge_code('partial', problem.pk, '.h')
        try:
            with open(partial_judge_code, 'r') as fp, open(partial_judge_header, 'r') as fp2:
                data['partial_judge_code'] = fp
                data['partial_judge_header'] = fp2
                response = self.JUDGE_CLIENT.post(target_url, data=data, follow=True)
        except (IOError, OSError):
            print "Something went wrong when reading partial judge files for testing..."
        data = POST_data_of_editing_Problem(self.JUDGE_USER, judge_type=Problem.SPECIAL)
        file_ex = get_problem_file_extension(problem)
        special_judge_code = create_judge_code('special', problem.pk, file_ex)
        try:
            with open(special_judge_code, 'r') as fp:
                data['special_judge_code'] = fp
                response = self.JUDGE_CLIENT.post(target_url, data=data, follow=True)
        except (IOError, OSError):
            print "Something went wrong when reading special judge files for testing..."
        uploaded_special_judge_code = '%s%s%s' % (SPECIAL_PATH, problem.pk, file_ex)
        uploaded_partial_judge_code = '%s%s%s' % (PARTIAL_PATH, problem.pk, file_ex)
        uploaded_partial_judge_header = '%s%s.h' % (PARTIAL_PATH, problem.pk)
        result = os.path.isfile(uploaded_special_judge_code)
        result2 = os.path.isfile(uploaded_partial_judge_code)
        result3 = os.path.isfile(uploaded_partial_judge_header)
        remove_file_if_exists(special_judge_code)
        remove_file_if_exists(uploaded_special_judge_code)
        remove_file_if_exists(partial_judge_code)
        remove_file_if_exists(uploaded_partial_judge_code)
        remove_file_if_exists(partial_judge_header)
        remove_file_if_exists(uploaded_partial_judge_header)
        self.assertTrue(result)
        self.assertFalse(result2)
        self.assertFalse(result3)


class Tester_Problem_rejudge(TestCase):
    """ test view 'problem:rejudge' """

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
        """ test view 'rejudge' """
        # 1.user does not login
        # Expectation: redirect to login page
        target_url = reverse('problem:rejudge')
        redirect_url = reverse('users:login') + '?next=' + target_url
        response = self.ANONYMOUS_CLIENT.get(target_url)
        self.assertRedirects(response, redirect_url)

    def test_02_problem_not_found(self):
        # 2.problem does not exist
        # Expectation: error 404
        pid = 1000000
        target_url = reverse('problem:rejudge')
        response = self.NORMAL_CLIENT.get(target_url, data={'pid':pid})
        self.assertEqual(response.status_code, 404)

    def test_03_permission(self):
        # 3.user has no permission
        # Expectation: error 403
        problem = create_problem(self.JUDGE_USER)
        target_url = reverse('problem:rejudge')
        response = self.NORMAL_CLIENT.get(target_url, data={'pid':problem.pk})
        self.assertEqual(response.status_code, 403)

    def test_04_rejudge(self):
        # 4.using GET method with argument 'pid', and problem exists, and user has permission
        # Expectation: rejudge all submissions with respect to this problem
        problem = create_problem(self.JUDGE_USER)
        target_url = reverse('problem:rejudge')
        users = [self.ADMIN_USER, self.JUDGE_USER, self.NORMAL_USER]
        submission_statuses = [Submission.ACCEPTED, Submission.NOT_ACCEPTED, Submission.COMPILE_ERROR,
                             Submission.RESTRICTED_FUNCTION, Submission.JUDGE_ERROR, Submission.JUDGING]
        for i in range(3):
            for j in range(2):
                create_submission(problem, users[i], submission_statuses[i*2+j])
        response = self.JUDGE_CLIENT.get(target_url, data={'pid':problem.pk})
        submissions = Submission.objects.filter(problem=problem)
        for submission in submissions:
            self.assertEqual(submission.status, Submission.WAIT)
