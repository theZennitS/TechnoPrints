# Copyright (c) 2026, Techno Print Chemicals Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def after_migrate():
	setup_techno_item_groups()
	setup_default_warehouses()
	setup_custom_fields()
	setup_default_workspace()


def setup_default_workspace():
	"""Ensures Administrator default workspace lands on Techno Chemicals and Sidebar has correct app association."""
	if frappe.db.exists("Sidebar", "Techno Chemicals"):
		frappe.db.set_value("Sidebar", "Techno Chemicals", "app", "techno_chemicals")
	if frappe.db.exists("User", "Administrator"):
		if not frappe.db.get_value("User", "Administrator", "default_workspace"):
			frappe.db.set_value("User", "Administrator", "default_workspace", "Techno Chemicals")



def setup_techno_item_groups():
	"""Creates default standard Chemical & Ink item groups under All Item Groups if missing."""
	if not frappe.db.exists("Item Group", "All Item Groups"):
		frappe.get_doc({"doctype": "Item Group", "item_group_name": "All Item Groups", "is_group": 1}).insert(
			ignore_permissions=True
		)

	if not frappe.db.exists("Item Group", "Techno Chemicals"):
		frappe.get_doc(
			{
				"doctype": "Item Group",
				"item_group_name": "Techno Chemicals",
				"parent_item_group": "All Item Groups",
				"is_group": 1,
			}
		).insert(ignore_permissions=True)

	child_groups = [
		{"item_group_name": "Finished Inks", "is_group": 0},
		{"item_group_name": "Solvents", "is_group": 0},
		{"item_group_name": "Resins & Varnishes", "is_group": 0},
		{"item_group_name": "Pigments", "is_group": 0},
		{"item_group_name": "Additives & Waxes", "is_group": 0},
		{"item_group_name": "Packaging Material", "is_group": 0},
	]

	for g in child_groups:
		if not frappe.db.exists("Item Group", g["item_group_name"]):
			frappe.get_doc(
				{
					"doctype": "Item Group",
					"item_group_name": g["item_group_name"],
					"parent_item_group": "Techno Chemicals",
					"is_group": g["is_group"],
				}
			).insert(ignore_permissions=True)


def setup_default_warehouses():
	"""Ensures default solvent and finished ink warehouses exist for active companies."""
	for company in frappe.get_all("Company", fields=["name", "abbr"]):
		parent_wh = f"All Warehouses - {company.abbr}"
		if not frappe.db.exists("Warehouse", parent_wh):
			continue

		warehouses = [
			("Solvent Tank Farm", 0),
			("Raw Material Chemical Store", 0),
			("Finished Inks Warehouse", 0),
			("QC Quarantine Storage", 0),
		]

		for wh_title, is_group in warehouses:
			wh_name = f"{wh_title} - {company.abbr}"
			if not frappe.db.exists("Warehouse", wh_name):
				frappe.get_doc(
					{
						"doctype": "Warehouse",
						"warehouse_name": wh_title,
						"parent_warehouse": parent_wh,
						"company": company.name,
						"is_group": is_group,
					}
				).insert(ignore_permissions=True)


def setup_custom_fields():
	"""Seeds custom link fields on standard ERPNext DocTypes for Ink Production & QC."""
	custom_fields = {
		"Work Order": [
			{
				"fieldname": "ink_sec_break",
				"label": "Ink Manufacturing Parameters",
				"fieldtype": "Section Break",
				"insert_after": "bom_no",
				"collapsible": 1,
			},
			{
				"fieldname": "ink_formulation",
				"label": "Ink Formulation Recipe",
				"fieldtype": "Link",
				"options": "Ink Formulation",
				"insert_after": "ink_sec_break",
			},
			{
				"fieldname": "target_substrate",
				"label": "Customer Target Substrate",
				"fieldtype": "Select",
				"options": "\nCorona Treated BOPP\nPlain BOPP\nPearlised BOPP\nMetallized PET\nPlain PET\nAluminum Blister Foil\nPolyethylene (LDPE/HDPE)\nKraft Paper\nShrink PVC / PET",
				"insert_after": "ink_formulation",
			},
			{
				"fieldname": "col_break_ink",
				"fieldtype": "Column Break",
				"insert_after": "target_substrate",
			},
			{
				"fieldname": "estimated_solvent_loss_pct",
				"label": "Solvent Loss / Evaporation (%)",
				"fieldtype": "Percent",
				"default": "3.5",
				"insert_after": "col_break_ink",
			},
		],
		"Delivery Note Item": [
			{
				"fieldname": "certificate_of_analysis",
				"label": "CoA Reference",
				"fieldtype": "Link",
				"options": "Certificate of Analysis",
				"insert_after": "batch_no",
				"in_list_view": 1,
				"columns": 2,
			},
		],
		"Sales Order Item": [
			{
				"fieldname": "shade_match_request",
				"label": "Shade Match Ref",
				"fieldtype": "Link",
				"options": "Shade Match Request",
				"insert_after": "item_code",
				"in_list_view": 1,
				"columns": 2,
			},
		],
	}
	create_custom_fields(custom_fields, update=True)

