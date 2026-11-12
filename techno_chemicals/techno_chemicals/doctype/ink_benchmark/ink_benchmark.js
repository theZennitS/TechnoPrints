// Copyright (c) 2026, Techno Print Chemicals Pvt Ltd and contributors
// For license information, please see license.txt

frappe.ui.form.on("Ink Benchmark", {
	setup: function(frm) {
		frm.set_query("item", function() {
			return {
				filters: {
					is_stock_item: 1,
					include_item_in_manufacturing: 1
				}
			};
		});
	},

	refresh: function(frm) {
		if (frm.doc.shade_match_request && frm.doc.item) {
			frm.dashboard.set_headline(
				__("Benchmark linked to Shade Match {0} for Target Item {1}.", [frm.doc.shade_match_request, frm.doc.item]),
				"blue"
			);
		}
	},

	shade_match_request: function(frm) {
		if (frm.doc.shade_match_request) {
			frappe.db.get_doc("Shade Match Request", frm.doc.shade_match_request).then(smr => {
				if (smr) {
					if (smr.commercial_item) {
						frm.set_value("item", smr.commercial_item);
					}
					if (smr.customer) {
						frm.set_value("customer", smr.customer);
					}
					if (smr.target_substrate) {
						frm.set_value("target_substrate", smr.target_substrate);
					}
					if (!frm.doc.benchmark_name) {
						frm.set_value("benchmark_name", (smr.target_shade_name || "Shade") + " Quality Benchmark");
					}

					// Auto-populate test parameters if empty
					if (!frm.doc.parameters || frm.doc.parameters.length === 0) {
						frm.clear_table("parameters");

						let delta_val = smr.delta_e_reading || 1.0;
						let row1 = frm.add_child("parameters");
						row1.parameter_name = "Delta E vs Swatch";
						row1.target_value = flt(delta_val, 2);
						row1.tolerance_min = 0.0;
						row1.tolerance_max = flt(delta_val + 0.5, 2);

						let visc_val = smr.viscosity_sec || 22.0;
						let row2 = frm.add_child("parameters");
						row2.parameter_name = "Press Viscosity (Sec)";
						row2.target_value = flt(visc_val, 1);
						row2.tolerance_min = flt(visc_val - 2.0, 1);
						row2.tolerance_max = flt(visc_val + 2.0, 1);

						let row3 = frm.add_child("parameters");
						row3.parameter_name = "Tape Adhesion";
						row3.target_value = 100.0;
						row3.tolerance_min = 95.0;
						row3.tolerance_max = 100.0;

						frm.refresh_field("parameters");
					}
				}
			});
		}
	}
});
