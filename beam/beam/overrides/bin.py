# Copyright (c) 2024, AgriTheory and contributors
# For license information, please see license.txt

import frappe


class Bin():
    pass

@frappe.whitelist()
@frappe.read_only()
def get_actual_qty(warehouse):
    actual_qty = frappe.db.get_all(
        "Bin",
        filters=[
            ["warehouse", "=", warehouse],
            ["actual_qty", ">", 0],
        ],
        fields=["item_code", "actual_qty", "valuation_rate"],
    )
    return actual_qty
