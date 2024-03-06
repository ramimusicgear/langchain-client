import pytest
from streamlit.testing.v1 import AppTest
from test_collection import filter_by_collection
from test_basic_filters import filter_by_basic_filters
from test_combine_filters import filter_by_combine_filters


def login_as_admin(at):
    # go to login page
    at.sidebar.button("to_login_btn").click().run(timeout=10)
    assert at.sidebar.button[1].label == "Back to Chat"

    # login as admin
    at.text_input[0].input("admin").run(timeout=10)
    at.text_input[1].input("22f52e80d").run(timeout=10)
    at.button("FormSubmitter:LoginForm-Login").click().run(timeout=30)

    return at


@pytest.mark.test_id("Test1")
def test_all():
    # Initialize the Streamlit app for testing from a file
    at = AppTest.from_file("main.py").run(timeout=30)
    at = login_as_admin(at)
    filter_by_collection(at)
    # filter_by_basic_filters(at)
    filter_by_combine_filters(at)


test_all()
