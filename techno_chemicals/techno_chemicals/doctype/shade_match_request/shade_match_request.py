# Copyright (c) 2026, Techno Print Chemicals Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cstr


class ShadeMatchRequest(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		commercial_bom: DF.Link | None
		commercial_item: DF.Link | None
		converter_feedback: DF.SmallText | None
		customer: DF.Link
		delta_e_reading: DF.Float
		matched_formulation: DF.Link | None
		naming_series: DF.Literal["SMR-.YYYY.-.#####"]
		pantone_reference: DF.Data | None
		sample_received_date: DF.Date | None
		status: DF.Literal["Sample Swatch Received", "Lab Drawdown Matching", "Trial Sample Dispatched", "Approved by Converter", "Revision Requested", "Rejected"]
		tape_adhesion_result: DF.Literal["Pass (100% Adhesion)", "Slight Flaking (<5%)", "Fail (Tape Lift)"]
		target_shade_name: DF.Data
		target_substrate: DF.Literal["Corona Treated BOPP", "Plain BOPP", "Pearlised BOPP", "Metallized PET", "Plain PET", "Aluminum Blister Foil", "Polyethylene (LDPE/HDPE)", "Kraft Paper", "Shrink PVC / PET"]
		testing_finished: DF.Check
		trial_dispatch_date: DF.Date | None
		trial_sample_qty_kg: DF.Float
		viscosity_sec: DF.Float
	# end: auto-generated types

	@frappe.whitelist()
	def create_finished_item(self):
		"""Creates an ERPNext Finished Ink Item from the approved shade match."""
		if self.commercial_item and frappe.db.exists("Item", self.commercial_item):
			return self.commercial_item

		# Generate a clean item code
		base_code = (self.pantone_reference or self.target_shade_name or "INK-SHADE").strip()
		base_code = "".join(c if c.isalnum() or c in "-_" else "-" for c in base_code).upper()

		item_code = base_code
		counter = 1
		while frappe.db.exists("Item", item_code):
			item_code = f"{base_code}-{counter}"
			counter += 1

		# Verify Item Group exists
		item_group = "Finished Inks"
		if not frappe.db.exists("Item Group", item_group):
			if frappe.db.exists("Item Group", "All Item Groups"):
				item_group = "All Item Groups"
			else:
				item_groups = frappe.get_all("Item Group", limit=1)
				item_group = item_groups[0].name if item_groups else "All Item Groups"

		item = frappe.get_doc({
			"doctype": "Item",
			"item_code": item_code,
			"item_name": self.target_shade_name or item_code,
			"item_group": item_group,
			"stock_uom": "Kg",
			"is_stock_item": 1,
			"include_item_in_manufacturing": 1,
			"description": f"Target Ink Shade: {self.target_shade_name} | Customer: {self.customer or 'General'} | Ref: {self.pantone_reference or ''}",
		})
		item.flags.ignore_permissions = True
		item.insert()

		self.commercial_item = item.name
		self.flags.ignore_permissions = True
		self.save()

		return item.name
