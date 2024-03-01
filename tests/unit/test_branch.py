import os
import pygit2
import yaml


def get_current_branch():
    stack_name = '/testing-Http-Api'
    repo_path = os.getcwd() + stack_name
    repo = pygit2.Repository(repo_path)
    current_branch = repo.head.shorthand
    return current_branch, repo_path


def test_stage_name_match():
    expected_stage, repo_path = get_current_branch()
    template_file = repo_path + '/template.yaml'
    with open(template_file, 'r') as f:
        template_data = yaml.safe_load(f)

    http_api_response = template_data.get('Resources', {}).get('HttpApi', {})
    actual_stage = http_api_response.get('Properties', {}).get('StageName')

    assert actual_stage == expected_stage,\
        f"Expected stage '{expected_stage}',\
        but found '{actual_stage}'."
