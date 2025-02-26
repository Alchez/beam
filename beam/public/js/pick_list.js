// Copyright (c) 2025, AgriTheory and contributors
// For license information, please see license.txt

frappe.ui.form.on('Pick List', {
	refresh(frm) {
		frm.add_custom_button('Reserve', () => {
			console.log(frm.doc.name)
		})
	},
})

function make_stock_reservation_entry() {}
