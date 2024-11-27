# Copyright (c) 2024, AgriTheory and contributors
# For license information, please see license.txt

import frappe
import pytest

from playwright.sync_api import expect


@pytest.fixture(scope="function", autouse=True)
def login(page):
	base_url = frappe.utils.get_url()
	page.goto(base_url)

	# visiting the home page redirects to login page
	page.get_by_role("textbox", name="Email").fill("Administrator")
	page.get_by_role("textbox", name="Password").fill("qwe")
	page.get_by_role("button", name="Login").click()
	yield


def test_login(page):
	# assert redirection to beam homepage after login
	base_url = frappe.utils.get_url()
	expect(page).to_have_url(f"{base_url}/beam#/")

	# context = new_context()
	# new_page = context.new_page()
	# new_page.goto(invoice_url)
	# new_page.wait_for_selector("#approve-btn")
	# approve_button = new_page.query_selector("#approve-btn")
	# approve_button.click()
	# new_page.wait_for_selector(".btn-modal-primary")
	# yes_button = new_page.query_selector(".btn-modal-primary")
	# yes_button.click()
