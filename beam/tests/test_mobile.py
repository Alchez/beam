# Copyright (c) 2024, AgriTheory and contributors
# For license information, please see license.txt

import re

import frappe
import pytest


@pytest.fixture(scope="function", autouse=True)
def login(page):
	page.set_default_timeout(5000)

	base_url = frappe.utils.get_url()
	page.goto(base_url)

	# visiting the home page redirects to login page
	page.get_by_role("textbox", name="Email").fill("Administrator")
	page.get_by_role("textbox", name="Password").fill("qwe")
	page.get_by_role("button", name="Login").click()
	yield


def test_ship(page):
	# assert redirection to beam homepage after login
	page.expect_navigation(url=re.compile("/beam#/"))

	# navigate to ship list page
	page.get_by_text("Ship").click()
	page.expect_navigation(url=re.compile("/beam#/ship"))

	# navigate to first purchase order in list
	page.get_by_role("listitem").first.click()
	page.expect_navigation(url=re.compile("/beam#/delivery-note/"))

	# TODO: scan barcode
	barcodes = frappe.get_all(
		"Item Barcode", filters={"parenttype": "Item", "parent": "Ambrosia Pie"}, pluck="barcode"
	)
	assert len(barcodes) > 0
