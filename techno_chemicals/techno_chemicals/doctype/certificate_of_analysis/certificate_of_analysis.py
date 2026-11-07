# Copyright (c) 2026, Techno Print Chemicals Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class CertificateofAnalysis(Document):
	def validate(self):
		if self.mfg_date and self.expiry_date and self.expiry_date <= self.mfg_date:
			frappe.throw(_("Best Before / Expiry Date must be after Date of Manufacture."))
