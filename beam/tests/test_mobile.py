# Copyright (c) 2024, AgriTheory and contributors
# For license information, please see license.txt

import re

import frappe
import pytest

from playwright.sync_api import expect


# NOTE: any navigation tests should be done using `expect(page).to_have_url` since
# `page.expect_navigation()` since the latter won't work with Beam's hash-based routes


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
	page.get_by_role("button", name="Login").click()  # this will redirect to `/beam`
	yield


@pytest.mark.parametrize("route", ["Receive", "Ship", "Manufacture"])
def test_scan_item_barcode(page, route):
	page.get_by_text(route).click()  # this will redirect to the Ship list page
	page.locator(
		"css=.beam_list-item"
	).first.click()  # this will redirect to the first Purchase Order in the list

	# find the first item in the order list
	item = page.locator("css=.box .beam_list-item").first
	item_name, *others = item.inner_text().split("\n")
	item_count = page.locator("css=.box .beam_item-count").first
	expect(item_count).to_have_text(re.compile("0/"))

	# ensure the item has barcodes
	barcodes = frappe.get_all(
		"Item Barcode", filters={"parenttype": "Item", "parent": item_name}, pluck="barcode"
	)
	assert len(barcodes) > 0

	# scan barcode
	with page.expect_request(
		lambda request: request.headers.get("x-frappe-cmd") == "beam.beam.scan.scan"
	):
		page.evaluate("barcode => scanner.simulate(window, barcode)", barcodes[0])
		expect(item_count).to_have_text(re.compile("1/"))
