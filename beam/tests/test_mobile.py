# Copyright (c) 2024, AgriTheory and contributors
# For license information, please see license.txt

import re

import frappe
import pytest

from playwright.sync_api import expect


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
	page.get_by_role("textbox", name="Email").fill("Administrator")
	page.get_by_role("textbox", name="Password").fill("qwe")
	page.get_by_role("button", name="Login").click()

	# NOTE: all navigation tests should be done using `expect(page).to_have_url` rather
	# than `page.expect_navigation()` because the latter does not work with hash-based routes
	yield


def test_ship(page):

	# assert redirection to beam homepage after login
	page.expect_navigation(url=re.compile("/beam"))

	# navigate to ship list page
	page.get_by_text("Ship").click()
	expect(page).to_have_url(re.compile("/beam#/ship"))

	# navigate to first purchase order in list
	page.get_by_role("listitem").first.click()
	expect(page).to_have_url(re.compile("/beam#/delivery-note"))

	# TODO: find item via the page
	barcodes = frappe.get_all(
		"Item Barcode", filters={"parenttype": "Item", "parent": "Ambrosia Pie"}, pluck="barcode"
	)
	assert len(barcodes) > 0

	def scan_request(request):
		return request.post_data_json.get("cmd") != "beam.beam.scan.scan"

	# TODO: scan barcode
	with page.expect_request(scan_request) as request_info:
		page.evaluate("barcode => scanner.simulate(window, barcode)", barcodes[0])
