// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

frappe.listview_settings["Payroll Entry"] = {
	has_indicator_for_draft: 1,
	onload(listview) {
		const standard_filters_wrapper = listview.page.page_form.find(".standard-filter-section");

		if (!listview.page.fields_dict.company) {
			listview.page.add_field(
				{
					fieldname: "company",
					label: __("Company"),
					fieldtype: "Link",
					options: "Company",
					condition: "=",
					is_filter: 1,
					onchange: () => listview.refresh(),
				},
				standard_filters_wrapper
			);
		}

		if (!listview.page.fields_dict.start_date) {
			listview.page.add_field(
				{
					fieldname: "start_date",
					label: __("Payroll Month"),
					fieldtype: "Date",
					condition: "=",
					is_filter: 1,
					onchange: () => listview.refresh(),
				},
				standard_filters_wrapper
			);
		}

		if (!listview.page.fields_dict.posting_date) {
			listview.page.add_field(
				{
					fieldname: "posting_date",
					label: __("Posting Date"),
					fieldtype: "Date",
					condition: "=",
					is_filter: 1,
					onchange: () => listview.refresh(),
				},
				standard_filters_wrapper
			);
		}
	},
	get_indicator(doc) {
		const status_color = {
			Draft: "red",
			Submitted: "blue",
			Queued: "orange",
			Failed: "red",
			Cancelled: "red",
		};
		return [__(doc.status), status_color[doc.status], "status,=," + doc.status];
	},
};
