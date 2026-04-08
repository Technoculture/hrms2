// Copyright (c) 2019, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

function register_ignored_standard_filters(listview, fieldnames) {
	const existing = listview.__tcr_ignored_standard_filters || [];
	listview.__tcr_ignored_standard_filters = [...new Set(existing.concat(fieldnames))];

	if (listview.__tcr_standard_filter_patch_applied) {
		return;
	}

	const original = listview.filter_area.get_standard_filters.bind(listview.filter_area);
	listview.filter_area.get_standard_filters = () => {
		const ignored = listview.__tcr_ignored_standard_filters || [];
		return original().filter((filter) => !ignored.includes(filter[1]));
	};
	listview.__tcr_standard_filter_patch_applied = true;
}

async function apply_l1_employee_filter(listview, l1_user, target_field = "employee") {
	await listview.filter_area.remove(target_field);
	if (!l1_user) {
		listview.refresh();
		return;
	}

	const response = await frappe.call({
		method: "tcr_erp.api.get_employee_ids_for_filters",
		args: { l1_manager: l1_user },
		freeze: false,
	});

	const employees = response.message || [];
	await listview.filter_area.add(
		listview.doctype,
		target_field,
		"in",
		employees.length ? employees : ["__no_employee__"]
	);
}

frappe.listview_settings["Leave Allocation"] = {
	onload(list_view) {
		const standard_filters_wrapper = list_view.page.page_form.find(".standard-filter-section");
		if (!list_view.page.fields_dict.tcr_l1_filter) {
			list_view.page.add_field(
				{
					fieldname: "tcr_l1_filter",
					label: __("L1"),
					fieldtype: "Link",
					options: "User",
					onchange: function () {
						apply_l1_employee_filter(list_view, this.get_value());
					},
				},
				standard_filters_wrapper
			);
		}
		register_ignored_standard_filters(list_view, ["tcr_l1_filter"]);
	},
	get_indicator(doc) {
		if (doc.status === "Expired") {
			return [__("Expired"), "gray", "expired, =, 1"];
		}
	},
};
