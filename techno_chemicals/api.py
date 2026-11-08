# Copyright (c) 2026, Techno Print Chemicals Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import flt


@frappe.whitelist()
def get_item_stock(item_code: str, warehouse: str | None = None) -> float:
	"""Returns the live available stock in Kg for an item.

	If warehouse is specified, returns stock from that warehouse;
	otherwise returns total stock across all warehouses.
	"""
	if not item_code:
		return 0.0

	filters = {"item_code": item_code}
	if warehouse:
		filters["warehouse"] = warehouse

	bins = frappe.get_all(
		"Bin",
		filters=filters,
		fields=["actual_qty"],
	)

	total_stock = sum(flt(b.actual_qty) for b in bins)
	return flt(total_stock, 2)


@frappe.whitelist()
def get_pigments_stock_summary() -> list[dict]:
	"""Returns a list of all pigment items with their current stock and reorder status."""
	pigment_items = frappe.get_all(
		"Item",
		filters={"item_group": "Pigments"},
		fields=["name as item_code", "item_name", "stock_uom"],
		order_by="item_name asc",
	)

	summary = []
	for p in pigment_items:
		stock = get_item_stock(p.item_code)
		reorder_level = flt(frappe.db.get_value("Item Reorder", {"parent": p.item_code}, "warehouse_reorder_level"))
		status = "Low Stock" if (reorder_level > 0 and stock <= reorder_level) else "Sufficient"
		summary.append({
			"item_code": p.item_code,
			"item_name": p.item_name,
			"stock_left": stock,
			"stock_uom": p.stock_uom,
			"reorder_level": reorder_level,
			"status": status,
		})

	return summary

