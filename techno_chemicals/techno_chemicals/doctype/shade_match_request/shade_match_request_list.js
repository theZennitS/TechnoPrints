// Copyright (c) 2026, Techno Print Chemicals Pvt Ltd and contributors
// For license information, please see license.txt

frappe.listview_settings["Shade Match Request"] = {
	formatters: {
		status: function(value) {
			if (!value) return "";
			return `<span class="filterable ellipsis" data-filter="status,=,${frappe.utils.escape_html(value)}" style="font-weight: 500;">${frappe.utils.escape_html(__(value))}</span>`;
		}
	}
};

