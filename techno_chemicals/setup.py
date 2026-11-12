# Copyright (c) 2026, Techno Print Chemicals Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def after_migrate():
	setup_techno_item_groups()
	setup_default_warehouses()
	setup_custom_fields()
	setup_default_workspace()
	setup_ink_operations()
	setup_ink_workstations()
	setup_ink_qc_standards()
	setup_qc_reference_type()
	setup_parameter_full_form()


def setup_parameter_full_form():
	"""Sets quick_entry = 0 on Quality Inspection Parameter so adding new parameter always opens full form."""
	if not frappe.db.exists("Property Setter", "Quality Inspection Parameter-main-quick_entry"):
		frappe.make_property_setter({
			"doctype": "Quality Inspection Parameter",
			"doctype_or_field": "DocType",
			"property": "quick_entry",
			"value": "0",
			"property_type": "Check",
		})
	else:
		frappe.db.set_value("Property Setter", "Quality Inspection Parameter-main-quick_entry", "value", "0")


def setup_qc_reference_type():
	"""Ensures 'Returns' is available in Quality Inspection reference_type options."""
	df = frappe.db.get_value("DocField", {"parent": "Quality Inspection", "fieldname": "reference_type"}, ["name", "options"], as_dict=True)
	if df and df.options and "Returns" not in df.options:
		new_options = df.options.strip() + "\nReturns"
		frappe.db.set_value("DocField", df.name, "options", new_options)
		frappe.clear_cache(doctype="Quality Inspection")


def setup_ink_operations():
	"""Seeds standard ink manufacturing process operations."""
	operations = [
		"Premixing & Dissolution",
		"Bead Milling (Dispersion)",
		"Let-down & Blending",
		"Viscosity & Shade Fine-Tuning",
		"Filtration & Drumming",
	]
	for op in operations:
		if not frappe.db.exists("Operation", op):
			frappe.get_doc({
				"doctype": "Operation",
				"name": op,
				"description": f"Standard {op} stage for liquid printing ink manufacture",
			}).insert(ignore_permissions=True)


def setup_ink_workstations():
	"""Seeds standard shop floor equipment and mills for ink production."""
	workstations = [
		{"name": "High Speed Disperser (HSD-01)", "rate": 350.0, "capacity": 1},
		{"name": "Horizontal Bead Mill (HBM-01)", "rate": 500.0, "capacity": 1},
		{"name": "Let-Down Blending Tank (LDT-01)", "rate": 250.0, "capacity": 1},
		{"name": "Filtration & Filling Station (FS-01)", "rate": 150.0, "capacity": 1},
	]
	for ws in workstations:
		if not frappe.db.exists("Workstation", ws["name"]):
			frappe.get_doc({
				"doctype": "Workstation",
				"workstation_name": ws["name"],
				"hour_rate": ws["rate"],
				"production_capacity": ws["capacity"],
			}).insert(ignore_permissions=True)


def setup_ink_qc_standards():
	"""Seeds standard Quality Inspection Parameters and liquid ink QC Template."""
	parameters = [
		{"name": "Viscosity (Ford Cup #4)", "description": "Efflux time at 25°C in seconds"},
		{"name": "Fineness of Grind (Hegman)", "description": "Dispersion fineness via Hegman gauge in microns"},
		{"name": "Shade Match (Delta E)", "description": "Total color difference under D65 spectrophotometer"},
		{"name": "Tape Adhesion Test", "description": "Cross-hatch cellophane tape pull test on substrate"},
		{"name": "Rub Resistance (Sutherland)", "description": "Sutherland rub cycles until ink film breakage"},
		{"name": "Gloss Level (60°)", "description": "Specular gloss at 60 degree geometry in Gloss Units"},
		{"name": "Drying Time (Sec)", "description": "Tack-free surface drying time under ambient draft in seconds"},
	]
	for p in parameters:
		if not frappe.db.exists("Quality Inspection Parameter", p["name"]):
			frappe.get_doc({
				"doctype": "Quality Inspection Parameter",
				"parameter": p["name"],
				"description": p["description"],
			}).insert(ignore_permissions=True)

	template_name = "Liquid Printing Ink QC Template"
	if not frappe.db.exists("Quality Inspection Template", template_name):
		frappe.get_doc({
			"doctype": "Quality Inspection Template",
			"quality_inspection_template_name": template_name,
			"item_quality_inspection_parameter": [
				{"specification": "Viscosity (Ford Cup #4)", "numeric": 1, "min_value": 18.0, "max_value": 26.0},
				{"specification": "Fineness of Grind (Hegman)", "numeric": 1, "min_value": 0.0, "max_value": 5.0},
				{"specification": "Shade Match (Delta E)", "numeric": 1, "min_value": 0.0, "max_value": 1.0},
				{"specification": "Tape Adhesion Test", "numeric": 0, "value": "Pass (100% Adhesion)"},
				{"specification": "Rub Resistance (Sutherland)", "numeric": 1, "min_value": 500.0, "max_value": 5000.0},
				{"specification": "Gloss Level (60°)", "numeric": 1, "min_value": 65.0, "max_value": 95.0},
				{"specification": "Drying Time (Sec)", "numeric": 1, "min_value": 6.0, "max_value": 14.0},
			],
		}).insert(ignore_permissions=True)



def setup_default_workspace():
	"""Ensures Administrator default workspace lands on Techno Chemicals and Sidebar has correct app association and items order."""
	import json
	import os

	sidebar_file = frappe.get_app_path(
		"techno_chemicals", "techno_chemicals", "sidebar", "techno_chemicals", "techno_chemicals.json"
	)
	if os.path.exists(sidebar_file):
		with open(sidebar_file, "r", encoding="utf-8") as f:
			sidebar_data = json.load(f)
		if frappe.db.exists("Sidebar", "Techno Chemicals"):
			doc = frappe.get_doc("Sidebar", "Techno Chemicals")
			doc.app = "techno_chemicals"
			doc.header_icon = sidebar_data.get("header_icon", "flask-conical")
			doc.set("items", [])
			for it in sidebar_data.get("items", []):
				doc.append("items", it)
			doc.flags.ignore_permissions = True
			doc.save()
		else:
			sidebar_data["doctype"] = "Sidebar"
			frappe.get_doc(sidebar_data).insert(ignore_permissions=True)

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
		"Delivery Note": [
			{
				"fieldname": "returns_sec_break",
				"label": "Customer Return Details",
				"fieldtype": "Section Break",
				"insert_after": "is_return",
				"depends_on": "eval:doc.is_return == 1",
				"collapsible": 1,
			},
			{
				"fieldname": "return_reason_category",
				"label": "Return Reason Category",
				"fieldtype": "Select",
				"options": "\nWrong Product Ordered by Customer\nWrong Product Dispatched by Plant\nAdhesion Failure / Peeling on Press\nOff Shade / Color Variation\nViscosity / Drying Issue\nGelling / Settling in Container\nRub / Scuff Resistance Failure\nPackaging Damaged / Leaking Drum\nExcess / Unused Stock Return\nOther",
				"insert_after": "returns_sec_break",
				"depends_on": "eval:doc.is_return == 1",
			},
			{
				"fieldname": "customer_notes",
				"label": "Return Reason / Customer Feedback Notes",
				"fieldtype": "Small Text",
				"insert_after": "return_reason_category",
				"depends_on": "eval:doc.is_return == 1",
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

