// Copyright (c) 2026, Techno Print Chemicals Pvt Ltd and contributors
// General Desk Enhancements

frappe.provide("frappe.ui.form");

function patch_quick_entry_parameter_group() {
	if (frappe.ui.form && frappe.ui.form.QuickEntryForm && !frappe.ui.form._quick_entry_param_patched) {
		frappe.ui.form._quick_entry_param_patched = true;
		const original_render_edit = frappe.ui.form.QuickEntryForm.prototype.render_edit_in_full_page_link;
		frappe.ui.form.QuickEntryForm.prototype.render_edit_in_full_page_link = function() {
			if (this.doctype === "Quality Inspection Parameter Group") {
				return;
			}
			if (original_render_edit) {
				return original_render_edit.apply(this, arguments);
			}
		};
	}
}

// Intercept make_quick_entry
let _original_make_quick_entry = frappe.ui.form.make_quick_entry;
Object.defineProperty(frappe.ui.form, "make_quick_entry", {
	configurable: true,
	enumerable: true,
	get: function() {
		return function(doctype, after_insert, init_callback, doc, force, skip_insert) {
			patch_quick_entry_parameter_group();
			let result = _original_make_quick_entry.apply(this, arguments);
			if (frappe.quick_entry && doctype === "Quality Inspection Parameter Group") {
				frappe.quick_entry.hide_full_form_button = true;
				if (frappe.quick_entry.custom_actions) {
					frappe.quick_entry.custom_actions.empty();
				}
			}
			return result;
		};
	},
	set: function(val) {
		_original_make_quick_entry = val;
	}
});

// Also patch immediately and on every page change
patch_quick_entry_parameter_group();
$(document).on("page-change ajaxComplete", function() {
	patch_quick_entry_parameter_group();
});
