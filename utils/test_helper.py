from django.test import Client

import os
import random
import string
import filecmp

from problem.models import Problem, Tag, Testcase, Submission
from users.models import User
from utils import config_info

TESTCASE_PATH = config_info.get_config('path', 'testcase_path')
TEST_PATH = ""

def create_test_directory(dir_name):
    TEST_PATH = dir_name
    if not os.path.isdir(TEST_PATH):
        os.makedirs(TEST_PATH)

def create_test_user(username, password, user_level):
    test_user = User.objects.create_user(username, password)
    test_user.user_level = user_level
    test_user.is_active = True
    test_user.save()

def create_test_admin_user():
    username = "test_admin"
    password = "test_admin"
    user_level = User.ADMIN
    create_test_user(username, password, user_level)

def create_test_judge_user():
    username = "test_judge"
    password = "test_judge"
    user_level = User.JUDGE
    create_test_user(username, password, user_level)

def create_test_normal_user():
    username = "test_user"
    password = "test_user"
    user_level = User.USER
    create_test_user(username, password, user_level)

def get_test_admin_user():
    return User.objects.get(username="test_admin")

def get_test_judge_user():
    return User.objects.get(username="test_judge")

def get_test_normal_user():
    return User.objects.get(username="test_user")

def get_test_admin_client():
    test_admin_client = Client()
    test_admin_client.login(username="test_admin", password="test_admin")
    return test_admin_client

def get_test_judge_client():
    test_judge_client = Client()
    test_judge_client.login(username="test_judge", password="test_judge")
    return test_judge_client

def get_test_normal_user_client():
    test_user_client = Client()
    test_user_client.login(username="test_user", password="test_user")
    return test_user_client

def create_problem(pname, owner):
    problem = Problem.objects.create(pname=pname, owner=owner)
    return problem

def random_word(length):
    return ''.join(random.choice(string.lowercase) for i in range(length)) 

def create_testcase_files(file_name, size=100, uploaded=False):
    if file_name == "":
        file_name = random_word(50)
    if not uploaded:
        path = TEST_PATH
    else:
        path = TESTCASE_PATH
    input_file_name = "%s%s.in" % (path, file_name)
    output_file_name = "%s%s.out" % (path, file_name)
    try:
        with open(input_file_name, 'w') as t_in:
            t_in.write(random_word(size))
        with open(output_file_name, 'w') as t_out:
            t_out.write(random_word(size))
    except (IOError, OSError):
        print "Failed to create testcase files for testing..."
    return file_name

def create_testcase(problem, time_limit, memory_limit, local_files=True, uploaded_files=False):
    testcase = Testcase.objects.create(problem=problem, time_limit=time_limit,
                                       memory_limit=memory_limit)
    if local_files:
        create_testcase_files(testcase.pk)
    if uploaded_files:
        create_testcase_files(testcase.pk, uploaded=True)
    return testcase

def remove_file_if_exists(file_name):
    try:
        if os.path.isfile(file_name):
            os.remove(file_name)
    except (IOError, OSError):
        print "Something went wrong when removing file: %s" % (file_name)

def remove_testcase_file(local_file_name, uploaded_file_name=None):
    local_input_file_name = "%s%s.in" % (TEST_PATH, local_file_name)
    local_output_file_name = "%s%s.out" % (TEST_PATH, local_file_name)
    remove_file_if_exists(local_input_file_name)
    remove_file_if_exists(local_output_file_name)
    if uploaded_file_name != None:
        uploaded_input_file_name = "%s%s.in" % (TESTCASE_PATH, uploaded_file_name)
        uploaded_output_file_name = "%s%s.out" % (TESTCASE_PATH, uploaded_file_name)
        remove_file_if_exists(uploaded_input_file_name)
        remove_file_if_exists(uploaded_output_file_name)

def compare_local_and_uploaded_testcase_files(local_file_name, uploaded_file_name):
    in_local = "%s%s.in" % (TEST_PATH, local_file_name)
    out_local = "%s%s.out" % (TEST_PATH, local_file_name)
    in_upload = "%s%s.in" % (TESTCASE_PATH, uploaded_file_name)
    out_upload = "%s%s.out" % (TESTCASE_PATH, uploaded_file_name)
    try:
        return filecmp.cmp(in_upload, in_local) and filecmp.cmp(out_upload, out_local)
    except (IOError, OSError):
        print "Something went wrong during file I/O..."
        print "Please make sure the path for testcase in nthuoj.cfg is an existing directory."
        print "Also, the user account of this machine that nthuoj depends on\
               should have permission to access and modify all the files in this directory."
        return False

def create_tag(tag_name, problem):
    new_tag, created = Tag.objects.get_or_create(tag_name=tag_name)
    #new_tag = Tag.objects.create(tag_name=tag_name)
    problem.tags.add(new_tag)
    problem.save()
    return new_tag

def create_submission(problem, user, status):
    submission = Submission.objects.create(problem=problem, user=user, status=status)
    return submission