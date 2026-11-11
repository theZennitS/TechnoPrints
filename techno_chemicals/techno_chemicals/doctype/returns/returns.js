// Copyright (c) 2026, Techno Print Chemicals Pvt Ltd and contributors
// For license information, please see license.txt

frappe.ui.form.on("Returns", {
	refresh: function(frm) {
		// Button: Raise for QC Check
		if (!frm.is_new() && !frm.doc.quality_inspection && frm.doc.status !== "Closed") {
			frm.add_custom_button(__("Raise for QC Check"), function() {
				frappe.call({
					method: "techno_chemicals.techno_chemicals.doctype.returns.returns.create_quality_inspection",
					args: {
						returns_name: frm.doc.name
					},
					callback: function(r) {
						if (r.message) {
							frappe.show_alert({
								message: __("Quality Inspection created: {0}", [r.message]),
								indicator: "green"
							});
							frappe.set_route("Form", "Quality Inspection", r.message);
						}
					}
				});
			}, __("Actions")).addClass("btn-primary");
		}

		// Button: Move to Finished Goods
		if (
			!frm.is_new() &&
			!frm.doc.stock_entry &&
			(frm.doc.qc_status === "QC Passed" ||
				frm.doc.disposition === "Restock to Finished Goods" ||
				frm.doc.status === "QC Passed - Ready for Restock")
		) {
			frm.add_custom_button(__("Move to Finished Goods"), function() {
				frappe.confirm(
					__(
						"Transfer {0} {1} of batch {2} from Quarantine to Finished Inks Warehouse?",
						[frm.doc.returned_qty, frm.doc.stock_uom || "Kg", frm.doc.batch_no]
					),
					function() {
						frappe.call({
							method: "techno_chemicals.techno_chemicals.doctype.returns.returns.transfer_to_finished_goods",
							args: {
								returns_name: frm.doc.name
							},
							freeze: true,
							freeze_message: __("Transferring batch to Finished Inks Warehouse..."),
							callback: function(r) {
								if (r.message) {
									frm.reload_doc();
									frappe.msgprint({
										title: __("Stock Restocked"),
										indicator: "green",
										message: __("Successfully transferred stock via Stock Entry: <a href='/app/stock-entry/{0}'><b>{0}</b></a>", [r.message])
									});
								}
							}
						});
					}
				);
			}, __("Actions")).addClass("btn-success");
		}
	},

	batch_no: function(frm) {
		if (!frm.doc.batch_no) return;
		frappe.db.get_value("Batch", frm.doc.batch_no, ["item", "stock_uom"]).then(r => {
			if (r.message) {
				if (r.message.item && !frm.doc.item_code) {
					frm.set_value("item_code", r.message.item);
				}
			}
		});
	}
});

