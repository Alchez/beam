# Copyright (c) 2024, AgriTheory and contributors
# For license information, please see license.txt

import frappe
import pytest


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
	# emulate an Android barcode scanner
	return {
		**browser_context_args,
		"viewport": {
			"width": 400,
			"height": 900,
		},
	}


@pytest.fixture(autouse=True)
def login(page):
	page.set_default_timeout(5000)

	base_url = frappe.utils.get_url()
	page.goto(base_url)

	# visiting the home page redirects to login page
	page.get_by_role("textbox", name="Email").fill("support@agritheory.dev")
	page.get_by_role("textbox", name="Password").fill("admin")
	page.get_by_role("button", name="Login").click()  # this will redirect to `/beam`
	yield
