# Copyright (c) 2024, AgriTheory and contributors
# For license information, please see license.txt

import re

import frappe
import pytest

from playwright.sync_api import expect


@pytest.mark.order(1)
def test_complete_partial_stock_entry(page):
	# navigate in the following order: Home -> Manufacture -> Work Order
	page.get_by_text("Manufacture").click()
	page.locator("css=.beam_list-item").first.click()

	# get the selected Work Order
	order_id = page.url.split("/")[-1]
	assert order_id

	# ensure there are no existing Stock Entries against this Work Order
	entry = frappe.db.exists(
		"Stock Entry",
		{"docstatus": 0, "work_order": order_id},
	)
	assert not entry

	# find the first item in the list
	item = page.locator("css=.box .beam_list-item").first
	item_code, *others = item.inner_text().split("\n")
	item_count = page.locator("css=.box .beam_item-count").first
	expect(item_count).to_have_text(re.compile("0/"))

	assert item_code == "Butter"

	# ensure that the item has barcodes
	barcodes = frappe.get_all(
		"Item Barcode", filters={"parenttype": "Item", "parent": item_code}, pluck="barcode"
	)
	assert len(barcodes) > 0

	# scan barcode and expect increment by 1
	with page.expect_request(
		lambda request: request.headers.get("x-frappe-cmd") == "beam.beam.scan.scan"
	):
		page.evaluate("barcode => scanner.simulate(window, barcode)", barcodes[0])
		expect(item_count).to_have_text(re.compile("1/"))

	# check that a draft Stock Entry is created
	page.get_by_text("SAVE", exact=True).click()
	entries = frappe.get_all(
		"Stock Entry",
		filters={"work_order": order_id},
		fields=["docstatus"],
	)
	assert len(entries) == 1
	assert entries[0]["docstatus"] == 0

	# check that the draft Purchase Receipt is submitted
	page.get_by_text("TRANSFER", exact=True).click()
	receipts = frappe.get_all(
		"Stock Entry",
		filters={"work_order": order_id},
		fields=["docstatus"],
	)
	assert len(receipts) == 1
	assert receipts[0]["docstatus"] == 1
