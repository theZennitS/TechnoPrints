// Copyright (c) 2026, Techno Print Chemicals Pvt Ltd and contributors
// For license information, please see license.txt

frappe.ui.form.on("Techno Chemicals Settings", {
	refresh(frm) {
		frm.set_intro(
			__(
				"Master operational rules, default ink warehouses, QC tolerances, and owner alert policies for Techno Print Chemicals."
			),
			"blue"
		);

		// Filter warehouses to matching company
		if (frm.doc.default_company) {
			const wh_filter = () => {
				return {
					filters: {
						company: frm.doc.default_company,
						is_group: 0,
					},
				};
			};

			frm.set_query("default_raw_material_warehouse", wh_filter);
			frm.set_query("default_wip_warehouse", wh_filter);
			frm.set_query("default_finished_goods_warehouse", wh_filter);
			frm.set_query("default_qc_quarantine_warehouse", wh_filter);
			frm.set_query("default_scrap_warehouse", wh_filter);
		}
	},
});

