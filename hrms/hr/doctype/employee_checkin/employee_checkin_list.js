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

frappe.listview_settings["Employee Checkin"] = {
	add_fields: ["offshift"],
	get_indicator: function (doc) {
		if (doc.offshift) {
			return [__("Off-Shift"), "yellow", "offshift,=,1"];
		}
	},
	onload: function (listview) {
		const standard_filters_wrapper = listview.page.page_form.find(".standard-filter-section");
		if (!listview.page.fields_dict.tcr_l1_filter) {
			listview.page.add_field(
				{
					fieldname: "tcr_l1_filter",
					label: __("L1"),
					fieldtype: "Link",
					options: "User",
					onchange: function () {
						apply_l1_employee_filter(listview, this.get_value());
					},
				},
				standard_filters_wrapper
			);
		}
		register_ignored_standard_filters(listview, ["tcr_l1_filter"]);

		listview.page.add_action_item(__("Fetch Shifts"), () => {
			const checkins = listview.get_checked_items().map((checkin) => checkin.name);
			frappe.call({
				method: "hrms.hr.doctype.employee_checkin.employee_checkin.bulk_fetch_shift",
				freeze: true,
				args: {
					checkins,
				},
			});
		});
	},
};
