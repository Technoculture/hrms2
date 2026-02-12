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

async function apply_employee_scope_filters(listview, l1_user, employee_status) {
	if (listview.__tcr_employee_scope_filter_applied) {
		await listview.filter_area.remove("employee");
		listview.__tcr_employee_scope_filter_applied = false;
	}

	if (!l1_user && !employee_status) {
		listview.refresh();
		return;
	}

	const response = await frappe.call({
		method: "tcr_erp.api.get_employee_ids_for_filters",
		args: {
			l1_manager: l1_user || null,
			employee_status: employee_status || null,
		},
		freeze: false,
	});

	const employees = response.message || [];
	await listview.filter_area.add(
		listview.doctype,
		"employee",
		"in",
		employees.length ? employees : ["__no_employee__"]
	);
	listview.__tcr_employee_scope_filter_applied = true;
}

frappe.listview_settings["Salary Slip"] = {
	onload: function (listview) {
		const standard_filters_wrapper = listview.page.page_form.find(".standard-filter-section");

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

		if (!listview.page.fields_dict.status) {
			listview.page.add_field(
				{
					fieldname: "status",
					label: __("Salary Slip Status"),
					fieldtype: "Select",
					options: "\nDraft\nSubmitted\nCancelled",
					condition: "=",
					is_filter: 1,
					onchange: () => listview.refresh(),
				},
				standard_filters_wrapper
			);
		}

		const get_l1_value = () => listview.page.fields_dict.tcr_l1_filter?.get_value();
		const get_employee_status_value = () =>
			listview.page.fields_dict.tcr_employee_status_filter?.get_value();

		if (!listview.page.fields_dict.tcr_l1_filter) {
			listview.page.add_field(
				{
					fieldname: "tcr_l1_filter",
					label: __("L1"),
					fieldtype: "Link",
					options: "User",
					onchange: function () {
						apply_employee_scope_filters(
							listview,
							this.get_value(),
							get_employee_status_value()
						);
					},
				},
				standard_filters_wrapper
			);
		}

		if (!listview.page.fields_dict.tcr_employee_status_filter) {
			listview.page.add_field(
				{
					fieldname: "tcr_employee_status_filter",
					label: __("Employee Status"),
					fieldtype: "Select",
					options: "\nActive\nInactive\nLeft\nSuspended",
					onchange: function () {
						apply_employee_scope_filters(listview, get_l1_value(), this.get_value());
					},
				},
				standard_filters_wrapper
			);
		}

		register_ignored_standard_filters(listview, [
			"tcr_l1_filter",
			"tcr_employee_status_filter",
		]);

		if (
			!has_common(frappe.user_roles, [
				"Administrator",
				"System Manager",
				"HR Manager",
				"HR User",
			])
		)
			return;

		listview.page.add_menu_item(__("Email Salary Slips"), () => {
			if (!listview.get_checked_items().length) {
				frappe.msgprint(__("Please select the salary slips to email"));
				return;
			}

			frappe.confirm(__("Are you sure you want to email the selected salary slips?"), () => {
				listview.call_for_selected_items(
					"hrms.payroll.doctype.salary_slip.salary_slip.enqueue_email_salary_slips",
				);
			});
		});
	},
};
