# Copyright (c) 2026, Techno Print Chemicals Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class InkFormulation(Document):
	def validate(self):
		self.calculate_totals()
		self.validate_percentage()

	def calculate_totals(self):
		total_pct = 0.0
		base_size = float(self.base_batch_size_kg or 100.0)
		for row in self.items:
			pct = float(row.percentage or 0.0)
			total_pct += pct
			row.quantity_kg = round((pct / 100.0) * base_size, 3)
		self.total_percentage = round(total_pct, 2)

	def validate_percentage(self):
		if abs(self.total_percentage - 100.0) > 0.05:
			frappe.throw(
				_(
					"Total formulation percentage must equal 100%. Current sum is {0}%. "
					"Please adjust component percentages."
				).format(self.total_percentage)
			)

	@frappe.whitelist()
	def create_bom(self):
		if self.docstatus != 1:
			frappe.throw(_("Formulation must be submitted before creating a BOM."))

		company = frappe.get_all("Company")[0].name
		bom = frappe.new_doc("BOM")
		bom.item = self.item_to_produce
		bom.quantity = float(self.base_batch_size_kg or 100.0)
		bom.company = company
		bom.is_active = 1
		bom.is_default = 1
		bom.with_operations = 0

		for item in self.items:
			bom.append("items", {
				"item_code": item.item_code,
				"qty": item.quantity_kg,
				"rate": 100.0,
				"uom": "Kg",
				"stock_uom": "Kg",
			})

		bom.insert(ignore_permissions=True)
		bom.submit()
		self.db_set("bom", bom.name)
		return bom.name
