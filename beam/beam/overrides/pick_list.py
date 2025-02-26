# Copyright (c) 2025, AgriTheory and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import safe_json_loads


@frappe.whitelist()
def make_stock_reservation_on_pl_save(doc, method=None):
	doc = safe_json_loads(doc) if isinstance(doc, str) else doc
	for row in doc.get("locations"):
		sre = frappe.new_doc("Stock Reservation Entry")
		sre.item_code = row.item_code
		sre.warehouse = row.warehouse
		sre.voucher_type = doc.doctype
		sre.voucher_no = doc.name
		sre.voucher_detail_no = row.name
		sre.available_qty = row.stock_qty
		sre.voucher_qty = row.stock_qty
		sre.stock_uom = row.stock_uom
		sre.reserved_qty = row.picked_qty
		sre.company = doc.company
		sre.flags.ignore_validate = True
		sre.save()
		sre.submit()
