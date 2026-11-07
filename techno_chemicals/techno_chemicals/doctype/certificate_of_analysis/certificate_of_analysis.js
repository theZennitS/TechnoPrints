// Copyright (c) 2026, Techno Print Chemicals Pvt Ltd and contributors
// For license information, please see license.txt

frappe.ui.form.on("Certificate of Analysis", {
	benchmark: function(frm) {
		if (!frm.doc.benchmark) return;
		frappe.call({
			method: "frappe.client.get",
			args: {
				doctype: "Ink Benchmark",
				name: frm.doc.benchmark
			},
			callback: function(r) {
				if (r.message && r.message.parameters) {
					frm.clear_table("readings");
					r.message.parameters.forEach(p => {
						let spec = "";
						if (p.target_value) {
							spec = `${p.min_value || ""} - ${p.max_value || ""} ${p.unit || ""} (Target: ${p.target_value})`.trim();
						} else if (p.expected_qualitative_result) {
							spec = p.expected_qualitative_result;
						} else {
							spec = `${p.min_value || ""} - ${p.max_value || ""} ${p.unit || ""}`.trim();
						}
						let row = frm.add_child("readings");
						row.parameter_name = p.parameter_name;
						row.test_method = p.test_method;
						row.specification_range = spec;
						row.actual_reading = p.target_value ? `${p.target_value} ${p.unit || ""}`.trim() : (p.expected_qualitative_result || "Pass");
						row.result = "Conforms";
					});
					frm.refresh_field("readings");
					if (r.message.target_substrate) {
						frm.set_value("target_substrate", r.message.target_substrate);
					}
					frappe.msgprint(__("Loaded test parameters from benchmark {0}", [frm.doc.benchmark]));
				}
			}
		});
	},
	batch_no: function(frm) {
		if (!frm.doc.batch_no) return;
		frappe.call({
			method: "frappe.client.get",
			args: {
				doctype: "Batch",
				name: frm.doc.batch_no
			},
			callback: function(r) {
				if (r.message) {
					if (r.message.item && !frm.doc.item_code) {
						frm.set_value("item_code", r.message.item);
					}
					if (r.message.manufacturing_date) {
						frm.set_value("mfg_date", r.message.manufacturing_date);
					}
					if (r.message.expiry_date) {
						frm.set_value("expiry_date", r.message.expiry_date);
					}
				}
			}
		});
	}
});
