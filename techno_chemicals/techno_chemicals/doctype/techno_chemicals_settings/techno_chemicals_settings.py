# Copyright (c) 2026, Techno Print Chemicals Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import validate_email_address


class TechnoChemicalsSettings(Document):
	def validate(self):
		self.validate_email()
		self.validate_tolerances()

	def validate_email(self):
		if self.owner_email:
			validate_email_address(self.owner_email, throw=True)

	def validate_tolerances(self):
		if self.default_delta_e_tolerance and self.default_delta_e_tolerance <= 0:
			frappe.throw(_("Standard Delta E Tolerance must be greater than 0"))

		if self.max_solvent_loss_pct and (self.max_solvent_loss_pct < 0 or self.max_solvent_loss_pct > 100):
			frappe.throw(_("Max Allowed Solvent Loss % must be between 0 and 100"))


def get_settings():
	"""Helper method to retrieve cached single doc settings."""
	return frappe.get_cached_doc("Techno Chemicals Settings")

