# Copyright (c) 2026, Techno Print Chemicals Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class Returns(Document):
	def validate(self):
		if self.returned_qty and self.returned_qty <= 0:
			frappe.throw(_("Returned Qty must be greater than zero."))


@frappe.whitelist()
def create_quality_inspection(returns_name):
	doc = frappe.get_doc("Returns", returns_name)

	template_name = "Liquid Printing Ink QC Template"
	if not frappe.db.exists("Quality Inspection Template", template_name):
		template_name = ""

	qi = frappe.new_doc("Quality Inspection")
	qi.inspection_type = "Incoming"
	qi.reference_type = "Returns"
	qi.reference_name = doc.name
	qi.item_code = doc.item_code
	qi.item_name = doc.item_name
	qi.batch_no = doc.batch_no
	qi.sample_size = doc.returned_qty or 1.0
	if template_name:
		qi.quality_inspection_template = template_name
	qi.flags.ignore_permissions = True
	qi.insert()

	doc.db_set("quality_inspection", qi.name)
	doc.db_set("status", "Under QC Check")

	return qi.name


@frappe.whitelist()
def transfer_to_finished_goods(returns_name):
	doc = frappe.get_doc("Returns", returns_name)

	company = (
		frappe.defaults.get_user_default("Company")
		or frappe.db.get_single_value("Global Defaults", "default_company")
		or frappe.db.get_value("Company", {}, "name")
	)
	abbr = frappe.db.get_value("Company", company, "abbr") if company else ""

	source_wh = f"QC Quarantine Storage - {abbr}" if abbr and frappe.db.exists("Warehouse", f"QC Quarantine Storage - {abbr}") else doc.warehouse
	target_wh = f"Finished Inks Warehouse - {abbr}" if abbr and frappe.db.exists("Warehouse", f"Finished Inks Warehouse - {abbr}") else ""

	if not target_wh or not frappe.db.exists("Warehouse", target_wh):
		target_wh = frappe.db.get_value("Warehouse", {"warehouse_name": ["like", "%Finished%"]}) or source_wh

	se = frappe.new_doc("Stock Entry")
	se.stock_entry_type = "Material Transfer"
	se.purpose = "Material Transfer"
	se.company = company
	se.append("items", {
		"item_code": doc.item_code,
		"s_warehouse": source_wh,
		"t_warehouse": target_wh,
		"qty": doc.returned_qty,
		"batch_no": doc.batch_no,
		"uom": doc.stock_uom or "Kg",
		"stock_uom": doc.stock_uom or "Kg",
		"conversion_factor": 1.0,
	})
	se.flags.ignore_permissions = True
	se.insert()
	se.submit()

	doc.db_set("stock_entry", se.name)
	doc.db_set("status", "Restocked to Finished Goods")
	doc.db_set("disposition", "Restock to Finished Goods")
	doc.db_set("warehouse", target_wh)

	return se.name


def on_quality_inspection_submit(doc, method=None):
	"""Syncs QC outcome back to the originating Returns document."""
	if doc.reference_type == "Returns" and doc.reference_name:
		if frappe.db.exists("Returns", doc.reference_name):
			ret = frappe.get_doc("Returns", doc.reference_name)
			ret.quality_inspection = doc.name
			if doc.status == "Accepted":
				ret.qc_status = "QC Passed"
				ret.status = "QC Passed - Ready for Restock"
				ret.disposition = "Restock to Finished Goods"
			else:
				ret.qc_status = "QC Failed"
				ret.status = "QC Failed - Action Required"
				ret.disposition = "Rework in Plant"
			ret.qc_findings = doc.remarks or f"Inspection status: {doc.status}"
			ret.flags.ignore_permissions = True
			ret.save()


def on_delivery_note_submit(doc, method=None):
	"""When a Sales Return Delivery Note (is_return=1) is submitted, automatically create Returns records."""
	if not doc.is_return:
		return

	for item in doc.items:
		existing = frappe.db.exists(
			"Returns",
			{
				"return_delivery_note": doc.name,
				"item_code": item.item_code,
				"batch_no": item.batch_no or "",
			},
		)
		if existing:
			continue

		ret = frappe.new_doc("Returns")
		ret.customer = doc.customer
		ret.posting_date = doc.posting_date or frappe.utils.today()
		ret.return_delivery_note = doc.name
		ret.original_delivery_note = getattr(doc, "return_against", "")
		ret.item_code = item.item_code
		ret.item_name = item.item_name
		ret.batch_no = item.batch_no or ""
		ret.returned_qty = abs(item.qty or 1.0)
		ret.stock_uom = item.stock_uom or item.uom or "Kg"
		ret.warehouse = item.warehouse or ""

		ret_reason = getattr(doc, "return_reason_category", None) or "Other"
		ret.return_reason_category = ret_reason
		ret.customer_notes = (
			getattr(doc, "customer_notes", None)
			or getattr(doc, "remarks", "")
			or f"Auto-created from Return Delivery Note {doc.name}"
		)
		ret.status = "Received in Quarantine"
		ret.qc_status = "Pending QC"
		ret.disposition = "Pending Inspection"
		ret.flags.ignore_permissions = True
		ret.insert()

		frappe.msgprint(
			_("Created Return record <a href='/app/returns/{0}'><b>{0}</b></a> for QC Inspection").format(ret.name),
			indicator="green",
		)


