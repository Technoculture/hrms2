import frappe
from frappe import _
from frappe.model import get_permitted_fields
from frappe.model.workflow import get_workflow_name
from frappe.query_builder import Order
from frappe.utils import add_days, date_diff, getdate, strip_html, get_time, time_diff_in_hours
import datetime
from erpnext.setup.doctype.employee.employee import get_holiday_list_for_employee

SUPPORTED_FIELD_TYPES = [
	"Link",
	"Select",
	"Small Text",
	"Text",
	"Long Text",
	"Text Editor",
	"Table",
	"Check",
	"Data",
	"Float",
	"Int",
	"Section Break",
	"Date",
	"Time",
	"Datetime",
	"Currency",
]


@frappe.whitelist()
def get_current_user_info() -> dict:
	current_user = frappe.session.user
	user = frappe.db.get_value(
		"User", current_user, ["name", "first_name", "full_name", "user_image"], as_dict=True
	)
	user["roles"] = frappe.get_roles(current_user)

	return user


@frappe.whitelist()
def get_current_employee_info() -> dict:
	current_user = frappe.session.user
	employee = frappe.db.get_value(
		"Employee",
		{"user_id": current_user, "status": "Active"},
		[
			"name",
			"first_name",
			"employee_name",
			"designation",
			"department",
			"company",
			"reports_to",
			"user_id",
		],
		as_dict=True,
	)
	return employee


@frappe.whitelist()
def get_all_employees() -> list[dict]:
	return frappe.get_all(
		"Employee",
		fields=[
			"name",
			"employee_name",
			"designation",
			"department",
			"company",
			"reports_to",
			"user_id",
			"image",
			"status",
		],
		limit=999999,
	)


# HR Settings
@frappe.whitelist()
def get_hr_settings() -> dict:
	settings = frappe.db.get_singles_dict("HR Settings", cast=True)
	return frappe._dict(
		allow_employee_checkin_from_mobile_app=settings.allow_employee_checkin_from_mobile_app,
		allow_geolocation_tracking=settings.allow_geolocation_tracking,
	)


# Notifications
@frappe.whitelist()
def get_unread_notifications_count() -> int:
	return frappe.db.count(
		"PWA Notification",
		{"to_user": frappe.session.user, "read": 0},
	)


@frappe.whitelist()
def mark_all_notifications_as_read() -> None:
	frappe.db.set_value(
		"PWA Notification",
		{"to_user": frappe.session.user, "read": 0},
		"read",
		1,
		update_modified=False,
	)


@frappe.whitelist()
def are_push_notifications_enabled() -> bool:
	try:
		return frappe.db.get_single_value("Push Notification Settings", "enable_push_notification_relay")
	except frappe.DoesNotExistError:
		# push notifications are not supported in the current framework version
		return False


# Attendance
@frappe.whitelist()
def get_attendance_calendar_events(employee: str, from_date: str, to_date: str) -> dict[str, str]:
	holidays = get_holidays_for_calendar(employee, from_date, to_date)
	attendance = get_attendance_for_calendar(employee, from_date, to_date)
	events = {}
	open_leave_applications = get_open_leave_application_dates(employee, from_date, to_date)
	open_leave_application_dates = [date for date in open_leave_applications.keys()]
	date = getdate(from_date)
	while date_diff(to_date, date) >= 0:
		date_str = date.strftime("%Y-%m-%d")
		if date in attendance:
			events[date_str] = attendance[date]
		elif date in holidays:
			events[date_str] = "Holiday"
		elif date_str in open_leave_application_dates:
			events[date_str] = open_leave_applications[date_str]["status"]
		date = add_days(date, 1)
	# iterate over the dates again to append Holiday if it's a holiday
	date = getdate(from_date)
	strf_holidays = [date.strftime("%Y-%m-%d") for date in holidays]
	while date_diff(to_date, date) >= 0:
		date_str = date.strftime("%Y-%m-%d")
		if date_str in strf_holidays:
			if events[date_str] == "FIRST HALF":
				events[date_str] = "FIRST HALF HOLIDAY"
			elif events[date_str] == "SECOND HALF":
				events[date_str] = "SECOND HALF HOLIDAY"
			elif events[date_str] == "FIRST HALF OPEN":
				events[date_str] = "FIRST HALF HOLIDAY"
			elif events[date_str] == "SECOND HALF OPEN":
				events[date_str] = "SECOND HALF HOLIDAY"
		date = add_days(date, 1)


	return events

def get_open_leave_application_dates(employee: str, from_date: str, to_date: str) -> list[str]:
	leave_applications = frappe.get_all("Leave Application", {"employee": employee, "status": "Open", "from_date": ["<=", to_date], "to_date": [">=", from_date]}, "*")
	dates = {}
	for leave_application in leave_applications:
		leave_dates = get_dates_from_date_range(leave_application.from_date, leave_application.to_date)
		# iterate over the dates and get more info about the leave for each date
		for date in leave_dates:
			dates[date] = {
				"leave_application": leave_application.name,
				"leave_type": leave_application.leave_type,
				"status": (leave_application.custom_half_day_session + " OPEN") if leave_application.half_day and str(leave_application.half_day_date) == date else "On Leave"
			}
	return dates

def get_dates_from_date_range(from_date: str, to_date: str) -> list[str]:
	dates = []
	date = getdate(from_date)
	while date_diff(to_date, date) >= 0:
		dates.append(date.strftime("%Y-%m-%d"))
		date = add_days(date, 1)
	return dates


def get_attendance_for_calendar(employee: str, from_date: str, to_date: str) -> list[dict[str, str]]:
	attendance = frappe.get_all(
		"Attendance",
		{"employee": employee, "docstatus": 1, "attendance_date": ["between", [from_date, to_date]]},
		["attendance_date", "status", "shift", "in_time", "out_time", "leave_application", "employee"],
	)
	# if status is half day, then check if it's first half or second half
	for d in attendance:
			d = get_attendance_for_date(d)
	return {d["attendance_date"]: d["status"] for d in attendance}

def get_attendance_for_date(d: any):

	# # check if the attendance is absent and still there is a leave application
	status_for_other_half = None
	if d["status"] == "Absent":
		leave_application = frappe.db.exists("Leave Application", {"employee": d["employee"], "from_date": ["<=", d["attendance_date"]], "to_date": [">=", d["attendance_date"]], "status": ["in", ["Approved", "Open"]], "docstatus": ["in", [0, 1]]})
		if leave_application:
			is_half_day = frappe.db.get_value("Leave Application", leave_application, "half_day") and frappe.db.get_value("Leave Application", leave_application, "half_day_date") == d["attendance_date"]
			if is_half_day:
				d["status"] = "Half Day"
				d["leave_application"] = leave_application
				status_for_other_half = "ABSENT"
			else:
				d["status"] = "On Leave"
	# check if the attendance is half day
	if d["status"] == "Half Day":
		# if there is any leave_application
		leave_application = d.get("leave_application")
		if leave_application:
			# get the leave application
			leave_session = frappe.db.get_value("Leave Application", leave_application, "custom_half_day_session")
			if leave_session == "FIRST HALF":
				d["status"] = "FIRST HALF"
				if status_for_other_half:
					d["status"] += " " + status_for_other_half
			elif leave_session == "SECOND HALF":
				d["status"] = "SECOND HALF"
				if status_for_other_half:
					d["status"] += " " + status_for_other_half
			return d
		# get the start time and end time of the shift
		shift = d.get("shift")
		if shift:
			shift = frappe.get_doc("Shift Type", d["shift"])
			start_time = shift.start_time
			end_time = shift.end_time
			in_time = get_time(d["in_time"])
			out_time = get_time(d["out_time"])

			# Convert timedelta to time if necessary
			if isinstance(start_time, datetime.timedelta):
				start_time = (datetime.datetime.min + start_time).time()
			if isinstance(end_time, datetime.timedelta):
				end_time = (datetime.datetime.min + end_time).time()
			# Calculate mid_day_time (center of shift)
			start_seconds = start_time.hour * 3600 + start_time.minute * 60 + start_time.second
			end_seconds = end_time.hour * 3600 + end_time.minute * 60 + end_time.second
			mid_seconds = (start_seconds + end_seconds) / 2
			mid_day_time = datetime.time(int(mid_seconds // 3600), int((mid_seconds % 3600) // 60), int(mid_seconds % 60))

			def time_diff_in_seconds(t1, t2):
				return abs((datetime.datetime.combine(datetime.date.today(), t2) - datetime.datetime.combine(datetime.date.today(), t1)).total_seconds())

			# Calculate durations in first and second half
			first_half_start = max(in_time, start_time)
			first_half_end = min(out_time, mid_day_time)
			first_half_duration = max(0, time_diff_in_seconds(first_half_start, first_half_end))

			second_half_start = max(in_time, mid_day_time)
			second_half_end = min(out_time, end_time)
			second_half_duration = max(0, time_diff_in_seconds(second_half_start, second_half_end))
			# Determine which half was less worked
			if first_half_duration >= second_half_duration:
				d["status"] = "SECOND HALF"
			else:
				d["status"] = "FIRST HALF"
		else:
			d["status"] = "SECOND HALF"
	return d


def get_holidays_for_calendar(employee: str, from_date: str, to_date: str) -> list[str]:
	if holiday_list := get_holiday_list_for_employee(employee, raise_exception=False):
		return frappe.get_all(
			"Holiday",
			filters={"parent": holiday_list, "holiday_date": ["between", [from_date, to_date]]},
			pluck="holiday_date",
		)

	return []


@frappe.whitelist()
def get_shift_requests(
	employee: str,
	approver_id: str | None = None,
	for_approval: bool = False,
	limit: int | None = None,
) -> list[dict]:
	filters = get_filters("Shift Request", employee, approver_id, for_approval)
	fields = [
		"name",
		"employee",
		"employee_name",
		"shift_type",
		"from_date",
		"to_date",
		"status",
		"approver",
		"docstatus",
		"creation",
	]

	if workflow_state_field := get_workflow_state_field("Shift Request"):
		fields.append(workflow_state_field)

	shift_requests = frappe.get_list(
		"Shift Request",
		fields=fields,
		filters=filters,
		order_by="creation desc",
		limit=limit,
	)

	if workflow_state_field:
		for application in shift_requests:
			application["workflow_state_field"] = workflow_state_field

	return shift_requests


@frappe.whitelist()
def get_attendance_requests(
	employee: str,
	for_approval: bool = False,
	limit: int | None = None,
) -> list[dict]:
	filters = get_filters("Attendance Request", employee, None, for_approval)
	fields = [
		"name",
		"reason",
		"employee",
		"employee_name",
		"from_date",
		"to_date",
		"include_holidays",
		"shift",
		"docstatus",
		"creation",
	]

	if workflow_state_field := get_workflow_state_field("Attendance Request"):
		fields.append(workflow_state_field)

	attendance_requests = frappe.get_list(
		"Attendance Request",
		fields=fields,
		filters=filters,
		order_by="creation desc",
		limit=limit,
	)

	if workflow_state_field:
		for application in attendance_requests:
			application["workflow_state_field"] = workflow_state_field

	return attendance_requests


def get_filters(
	doctype: str,
	employee: str,
	approver_id: str | None = None,
	for_approval: bool = False,
) -> dict:
	filters = frappe._dict()
	if for_approval:
		filters.docstatus = 0
		filters.employee = ("!=", employee)

		if workflow := get_workflow(doctype):
			allowed_states = get_allowed_states_for_workflow(workflow, approver_id)
			filters[workflow.workflow_state_field] = ("in", allowed_states)
		else:
			approver_field_map = {
				"Shift Request": "approver",
				"Leave Application": "leave_approver",
				"Expense Claim": "expense_approver",
			}
			filters.status = "Open" if doctype == "Leave Application" else "Draft"
			if approver_id:
				filters[approver_field_map[doctype]] = approver_id
	else:
		filters.docstatus = ("!=", 2)
		filters.employee = employee

	return filters


@frappe.whitelist()
def get_shift_request_approvers(employee: str) -> str | list[str]:
	shift_request_approver, department = frappe.get_cached_value(
		"Employee",
		employee,
		["shift_request_approver", "department"],
	)

	department_approvers = []
	if department:
		department_approvers = get_department_approvers(department, "shift_request_approver")
		if not shift_request_approver:
			shift_request_approver = frappe.db.get_value(
				"Department Approver",
				{"parent": department, "parentfield": "shift_request_approver", "idx": 1},
				"approver",
			)

	shift_request_approver_name = frappe.db.get_value("User", shift_request_approver, "full_name", cache=True)

	if shift_request_approver and shift_request_approver not in [
		approver.name for approver in department_approvers
	]:
		department_approvers.insert(
			0, {"name": shift_request_approver, "full_name": shift_request_approver_name}
		)

	return department_approvers


@frappe.whitelist()
def get_shifts(employee: str) -> list[dict[str, str]]:
	ShiftAssignment = frappe.qb.DocType("Shift Assignment")
	ShiftType = frappe.qb.DocType("Shift Type")
	return (
		frappe.qb.from_(ShiftAssignment)
		.join(ShiftType)
		.on(ShiftAssignment.shift_type == ShiftType.name)
		.select(
			ShiftAssignment.name,
			ShiftAssignment.shift_type,
			ShiftAssignment.start_date,
			ShiftAssignment.end_date,
			ShiftType.start_time,
			ShiftType.end_time,
		)
		.where(
			(ShiftAssignment.employee == employee)
			& (ShiftAssignment.status == "Active")
			& (ShiftAssignment.docstatus == 1)
		)
		.orderby(ShiftAssignment.start_date, order=Order.asc)
	).run(as_dict=True)


# Leaves and Holidays
@frappe.whitelist()
def get_leave_applications(
	employee: str,
	approver_id: str | None = None,
	for_approval: bool = False,
	limit: int | None = None,
) -> list[dict]:
	filters = get_filters("Leave Application", employee, approver_id, for_approval)
	fields = [
		"name",
		"posting_date",
		"employee",
		"employee_name",
		"leave_type",
		"status",
		"from_date",
		"to_date",
		"half_day",
		"half_day_date",
		"description",
		"total_leave_days",
		"leave_balance",
		"leave_approver",
		"posting_date",
		"creation",
	]

	if workflow_state_field := get_workflow_state_field("Leave Application"):
		fields.append(workflow_state_field)

	applications = frappe.get_list(
		"Leave Application",
		fields=fields,
		filters=filters,
		order_by="posting_date desc",
		limit=limit,
	)

	if workflow_state_field:
		for application in applications:
			application["workflow_state_field"] = workflow_state_field

	return applications


@frappe.whitelist()
def get_leave_balance_map(employee: str) -> dict[str, dict[str, float]]:
	"""
	Returns a map of leave type and balance details like:
	{
	        'Casual Leave': {'allocated_leaves': 10.0, 'balance_leaves': 5.0},
	        'Earned Leave': {'allocated_leaves': 3.0, 'balance_leaves': 3.0},
	}
	"""
	from hrms.hr.doctype.leave_application.leave_application import get_leave_details

	date = getdate()
	leave_map = {}

	leave_details = get_leave_details(employee, date)
	allocation = leave_details["leave_allocation"]
	company = frappe.db.get_value("Employee", employee, "company")
	leave_period = frappe.get_doc("Leave Period", {"company": company, "is_active": 1})

	for leave_type, details in allocation.items():
		leave_applications = frappe.db.get_all("Leave Application", {"employee": employee, "status": ["in", ["Approved", "Open"]], "leave_type": leave_type, "from_date": ["<=", leave_period.to_date], "to_date": [">=", leave_period.from_date]}, ["total_leave_days", "leave_type"])
		# Calculate total leave days consumed
		total_leave_days = sum(application.total_leave_days for application in leave_applications)
		leave_map[leave_type] = {
			"allocated_leaves": details.get("total_leaves"),
			"balance_leaves": details.get("total_leaves") - total_leave_days,
		}

	return leave_map

@frappe.whitelist()
def get_my_lwp_consumption(employee: str) -> dict:
	from hrms.hr.doctype.leave_application.leave_application import get_leave_details

	date = getdate()
	# Retrieve active leave period for the company of employee
	company = frappe.db.get_value("Employee", employee, "company")
	leave_period = frappe.get_doc("Leave Period", {"company": company, "is_active": 1})

	if not leave_period:
		return {}

	# get max_allowed_lwp
	lwps = frappe.get_list("Leave Type", filters={"is_lwp": 1}, pluck="name")

	leave_map = {}

	if not lwps:
		leave_map['Leave Without Pay'] =  {
			"allocated_leaves": 0,
			"balance_leaves": total_leave_days,
		}

	# Get leave application for the leave period
	leave_applications = frappe.db.get_all("Leave Application", {"employee": employee, "status": ["in", ["Approved", "Open"]], "leave_type": ["in", lwps], "from_date": ["<=", leave_period.to_date], "to_date": [">=", leave_period.from_date]}, ["total_leave_days", "leave_type"])

	# Calculate total leave days consumed
	total_leave_days = sum(application.total_leave_days for application in leave_applications)

	max_allowed_lwps = frappe.get_value("Leave Type", lwps[0], "max_leaves_allowed")

	leave_map[lwps[0]] = {
			"allocated_leaves": max_allowed_lwps,
			"balance_leaves": max_allowed_lwps - total_leave_days,
		}
	return leave_map


@frappe.whitelist()
def get_holidays_for_employee(employee: str) -> list[dict]:
	holiday_list = get_holiday_list_for_employee(employee, raise_exception=False)
	if not holiday_list:
		return []

	Holiday = frappe.qb.DocType("Holiday")
	holidays = (
		frappe.qb.from_(Holiday)
		.select(Holiday.name, Holiday.holiday_date, Holiday.description)
		.where((Holiday.parent == holiday_list) & (Holiday.weekly_off == 0))
		.orderby(Holiday.holiday_date, order=Order.asc)
	).run(as_dict=True)

	for holiday in holidays:
		holiday["description"] = strip_html(holiday["description"] or "").strip()

	return holidays


@frappe.whitelist()
def get_leave_approval_details(employee: str) -> dict:
	leave_approver, department = frappe.get_cached_value(
		"Employee",
		employee,
		["leave_approver", "department"],
	)

	if not leave_approver and department:
		leave_approver = frappe.db.get_value(
			"Department Approver",
			{"parent": department, "parentfield": "leave_approvers", "idx": 1},
			"approver",
		)

	leave_approver_name = frappe.db.get_value("User", leave_approver, "full_name", cache=True)
	department_approvers = get_department_approvers(department, "leave_approvers")

	if leave_approver and leave_approver not in [approver.name for approver in department_approvers]:
		department_approvers.append({"name": leave_approver, "full_name": leave_approver_name})

	return dict(
		leave_approver=leave_approver,
		leave_approver_name=leave_approver_name,
		department_approvers=department_approvers,
		is_mandatory=frappe.db.get_single_value(
			"HR Settings", "leave_approver_mandatory_in_leave_application"
		),
	)


def get_department_approvers(department: str, parentfield: str) -> list[str]:
	if not department:
		return []

	department_details = frappe.db.get_value("Department", department, ["lft", "rgt"], as_dict=True)
	departments = frappe.get_all(
		"Department",
		filters={
			"lft": ("<=", department_details.lft),
			"rgt": (">=", department_details.rgt),
			"disabled": 0,
		},
		pluck="name",
	)

	Approver = frappe.qb.DocType("Department Approver")
	User = frappe.qb.DocType("User")
	department_approvers = (
		frappe.qb.from_(User)
		.join(Approver)
		.on(Approver.approver == User.name)
		.select(User.name.as_("name"), User.full_name.as_("full_name"))
		.where((Approver.parent.isin(departments)) & (Approver.parentfield == parentfield))
	).run(as_dict=True)

	return department_approvers


@frappe.whitelist()
def get_leave_types(employee: str, date: str) -> list:
	from hrms.hr.doctype.leave_application.leave_application import get_leave_details

	date = date or getdate()

	leave_details = get_leave_details(employee, date)
	leave_types = list(leave_details["leave_allocation"].keys()) + leave_details["lwps"]

	return leave_types


# Expense Claims
@frappe.whitelist()
def get_expense_claims(
	employee: str,
	approver_id: str | None = None,
	for_approval: bool = False,
	limit: int | None = None,
) -> list[dict]:
	filters = get_filters("Expense Claim", employee, approver_id, for_approval)
	fields = [
		"`tabExpense Claim`.name",
		"`tabExpense Claim`.posting_date",
		"`tabExpense Claim`.employee",
		"`tabExpense Claim`.employee_name",
		"`tabExpense Claim`.approval_status",
		"`tabExpense Claim`.status",
		"`tabExpense Claim`.expense_approver",
		"`tabExpense Claim`.total_claimed_amount",
		"`tabExpense Claim`.posting_date",
		"`tabExpense Claim`.company",
		"`tabExpense Claim`.creation",
		"`tabExpense Claim Detail`.expense_type",
		"count(`tabExpense Claim Detail`.expense_type) as total_expenses",
	]

	if workflow_state_field := get_workflow_state_field("Expense Claim"):
		fields.append(workflow_state_field)

	claims = frappe.get_list(
		"Expense Claim",
		fields=fields,
		filters=filters,
		order_by="`tabExpense Claim`.posting_date desc",
		group_by="`tabExpense Claim`.name",
		limit=limit,
	)

	if workflow_state_field:
		for claim in claims:
			claim["workflow_state_field"] = workflow_state_field

	return claims


@frappe.whitelist()
def get_expense_claim_summary(employee: str) -> dict:
	from frappe.query_builder.functions import Sum

	Claim = frappe.qb.DocType("Expense Claim")

	pending_claims_case = (
		frappe.qb.terms.Case().when(Claim.approval_status == "Draft", Claim.total_claimed_amount).else_(0)
	)
	sum_pending_claims = Sum(pending_claims_case).as_("total_pending_amount")

	approved_claims_case = (
		frappe.qb.terms.Case()
		.when(Claim.approval_status == "Approved", Claim.total_sanctioned_amount)
		.else_(0)
	)
	sum_approved_claims = Sum(approved_claims_case).as_("total_approved_amount")

	rejected_claims_case = (
		frappe.qb.terms.Case()
		.when(Claim.approval_status == "Rejected", Claim.total_sanctioned_amount)
		.else_(0)
	)
	sum_rejected_claims = Sum(rejected_claims_case).as_("total_rejected_amount")

	summary = (
		frappe.qb.from_(Claim)
		.select(
			sum_pending_claims,
			sum_approved_claims,
			sum_rejected_claims,
			Claim.company,
		)
		.where((Claim.docstatus != 2) & (Claim.employee == employee))
	).run(as_dict=True)[0]

	currency = frappe.db.get_value("Company", summary.company, "default_currency")
	summary["currency"] = currency

	return summary


@frappe.whitelist()
def get_expense_type_description(expense_type: str) -> str:
	return frappe.db.get_value("Expense Claim Type", expense_type, "description")


@frappe.whitelist()
def get_expense_claim_types() -> list[dict]:
	ClaimType = frappe.qb.DocType("Expense Claim Type")

	return (frappe.qb.from_(ClaimType).select(ClaimType.name, ClaimType.description)).run(as_dict=True)


@frappe.whitelist()
def get_expense_approval_details(employee: str) -> dict:
	expense_approver, department = frappe.get_cached_value(
		"Employee",
		employee,
		["expense_approver", "department"],
	)

	if not expense_approver and department:
		expense_approver = frappe.db.get_value(
			"Department Approver",
			{"parent": department, "parentfield": "expense_approvers", "idx": 1},
			"approver",
		)

	expense_approver_name = frappe.db.get_value("User", expense_approver, "full_name", cache=True)
	department_approvers = get_department_approvers(department, "expense_approvers")

	if expense_approver and expense_approver not in [approver.name for approver in department_approvers]:
		department_approvers.append({"name": expense_approver, "full_name": expense_approver_name})

	return dict(
		expense_approver=expense_approver,
		expense_approver_name=expense_approver_name,
		department_approvers=department_approvers,
		is_mandatory=frappe.db.get_single_value("HR Settings", "expense_approver_mandatory_in_expense_claim"),
	)


# Employee Advance
@frappe.whitelist()
def get_employee_advance_balance(employee: str) -> list[dict]:
	Advance = frappe.qb.DocType("Employee Advance")

	advances = (
		frappe.qb.from_(Advance)
		.select(
			Advance.name,
			Advance.employee,
			Advance.status,
			Advance.purpose,
			Advance.paid_amount,
			(Advance.paid_amount - (Advance.claimed_amount + Advance.return_amount)).as_("balance_amount"),
			Advance.posting_date,
			Advance.currency,
		)
		.where(
			(Advance.docstatus == 1)
			& (Advance.paid_amount)
			& (Advance.employee == employee)
			# don't need claimed & returned advances, only partly or completely paid ones
			& (Advance.status.isin(["Paid", "Unpaid"]))
		)
		.orderby(Advance.posting_date, order=Order.desc)
	).run(as_dict=True)

	return advances


@frappe.whitelist()
def get_advance_account(company: str) -> str | None:
	return frappe.db.get_value("Company", company, "default_employee_advance_account", cache=True)


# Company
@frappe.whitelist()
def get_company_currencies() -> dict:
	Company = frappe.qb.DocType("Company")
	Currency = frappe.qb.DocType("Currency")

	query = (
		frappe.qb.from_(Company)
		.join(Currency)
		.on(Company.default_currency == Currency.name)
		.select(
			Company.name,
			Company.default_currency,
			Currency.name.as_("currency"),
			Currency.symbol.as_("symbol"),
		)
	)

	companies = query.run(as_dict=True)
	return {company.name: (company.default_currency, company.symbol) for company in companies}


@frappe.whitelist()
def get_currency_symbols() -> dict:
	Currency = frappe.qb.DocType("Currency")

	currencies = (frappe.qb.from_(Currency).select(Currency.name, Currency.symbol)).run(as_dict=True)

	return {currency.name: currency.symbol or currency.name for currency in currencies}


@frappe.whitelist()
def get_company_cost_center_and_expense_account(company: str) -> dict:
	return frappe.db.get_value(
		"Company", company, ["cost_center", "default_expense_claim_payable_account"], as_dict=True
	)


# Form View APIs
@frappe.whitelist()
def get_doctype_fields(doctype: str) -> list[dict]:
	fields = frappe.get_meta(doctype).fields
	return [
		field
		for field in fields
		if field.fieldtype in SUPPORTED_FIELD_TYPES and field.fieldname != "amended_from"
	]


@frappe.whitelist()
def get_doctype_states(doctype: str) -> dict:
	states = frappe.get_meta(doctype).states
	return {state.title: state.color.lower() for state in states}


# File
@frappe.whitelist()
def get_attachments(dt: str, dn: str):
	from frappe.desk.form.load import get_attachments

	return get_attachments(dt, dn)


@frappe.whitelist()
def upload_base64_file(content, filename, dt=None, dn=None, fieldname=None):
	import base64
	import io
	from mimetypes import guess_type

	from PIL import Image, ImageOps

	from frappe.handler import ALLOWED_MIMETYPES

	decoded_content = base64.b64decode(content)
	content_type = guess_type(filename)[0]
	if content_type not in ALLOWED_MIMETYPES:
		frappe.throw(_("You can only upload JPG, PNG, PDF, TXT or Microsoft documents."))

	if content_type.startswith("image/jpeg"):
		# transpose the image according to the orientation tag, and remove the orientation data
		with Image.open(io.BytesIO(decoded_content)) as image:
			transpose_img = ImageOps.exif_transpose(image)
			# convert the image back to bytes
			file_content = io.BytesIO()
			transpose_img.save(file_content, format="JPEG")
			file_content = file_content.getvalue()
	else:
		file_content = decoded_content

	return frappe.get_doc(
		{
			"doctype": "File",
			"attached_to_doctype": dt,
			"attached_to_name": dn,
			"attached_to_field": fieldname,
			"folder": "Home",
			"file_name": filename,
			"content": file_content,
			"is_private": 1,
		}
	).insert()


@frappe.whitelist()
def delete_attachment(filename: str):
	frappe.delete_doc("File", filename)


@frappe.whitelist()
def download_salary_slip(name: str):
	import base64

	from frappe.utils.print_format import download_pdf

	default_print_format = frappe.get_meta("Salary Slip").default_print_format or "Standard"

	try:
		download_pdf("Salary Slip", name, format=default_print_format)
	except Exception:
		frappe.throw(_("Failed to download Salary Slip PDF"))

	base64content = base64.b64encode(frappe.local.response.filecontent)
	content_type = frappe.local.response.type

	return f"data:{content_type};base64," + base64content.decode("utf-8")


# Workflow
@frappe.whitelist()
def get_workflow(doctype: str) -> dict:
	workflow = get_workflow_name(doctype)
	if not workflow:
		return frappe._dict()
	return frappe.get_doc("Workflow", workflow)


def get_workflow_state_field(doctype: str) -> str | None:
	workflow_name = get_workflow_name(doctype)
	if not workflow_name:
		return None

	override_status, workflow_state_field = frappe.db.get_value(
		"Workflow",
		workflow_name,
		["override_status", "workflow_state_field"],
	)
	# NOTE: checkbox labelled 'Don't Override Status' is named override_status hence the inverted logic
	if not override_status:
		return workflow_state_field
	return None


def get_allowed_states_for_workflow(workflow: dict, user_id: str) -> list[str]:
	user_roles = frappe.get_roles(user_id)
	return [transition.state for transition in workflow.transitions if transition.allowed in user_roles]


# Permissions
@frappe.whitelist()
def get_permitted_fields_for_write(doctype: str) -> list[str]:
	return get_permitted_fields(doctype, permission_type="write")

@frappe.whitelist()	
def get_attendance_history(employee: str, month: str) -> list[dict]:
	"""
	Get detailed attendance history for an employee for a specific month.
	Gathers data from Employee Checkin, Attendance, Shift Assignment, Shift Type,
	and Attendance Regularization doctypes.
	
	Args:
		employee (str): Employee ID
		month (str): Month in YYYY-MM format
		
	Returns:
		list[dict]: List of attendance records with detailed information
	"""
	import frappe
	from frappe.utils import getdate, get_first_day, get_last_day, add_days, format_time, time_diff_in_hours, format_datetime
	from datetime import datetime, timedelta
	import calendar

	# Parse month and get date range
	try:
		year, month_num = map(int, month.split('-'))
		start_date = get_first_day(getdate(f"{year}-{month_num:02d}-01"))
		end_date = get_last_day(getdate(f"{year}-{month_num:02d}-01"))
		# if year and month is the current month and year, then restrict end_date to today
		if year == getdate().year and month_num == getdate().month:
			end_date = getdate()
	except (ValueError, TypeError):
		frappe.throw("Invalid month format. Use YYYY-MM format.")
	
	attendance_history = []
	holidays = get_holidays(employee, start_date, end_date)
	
	# Iterate through each day of the month
	current_date = start_date
	while current_date <= end_date:
		date_str = current_date.strftime('%Y-%m-%d')
		
		# Get attendance record for this date
		attendance = frappe.db.get_value(
			"Attendance",
			{
				"employee": employee,
				"attendance_date": current_date,
				"docstatus": 1
			},
			[
				"status", "working_hours", "late_entry", "early_exit", 
				"in_time", "out_time", "shift", "leave_type"
			],
			as_dict=True
		)
		
		# Get shift assignment for this date using SQL query
		shift_assignment = frappe.db.sql("""
			SELECT shift_type, start_date, end_date
			FROM `tabShift Assignment`
			WHERE employee = %s 
				AND start_date <= %s 
				AND (end_date >= %s OR end_date IS NULL)
				AND docstatus = 1 
			ORDER BY start_date DESC
			LIMIT 1
		""", (employee, current_date, current_date), as_dict=True)
		
		shift_assignment = shift_assignment[0] if shift_assignment else None
		
		# Get shift type details
		shift_type = None
		shift_start_time = None
		shift_end_time = None
		shift_name = None
		
		if shift_assignment:
			shift_type_doc = frappe.db.get_value(
				"Shift Type",
				shift_assignment.shift_type,
				["name", "start_time", "end_time"],
				as_dict=True
			)
			if shift_type_doc:
				shift_type = shift_type_doc
				shift_name = shift_type_doc.name
				shift_start_time = format_time(shift_type_doc.start_time, format_string="hh:mm") if shift_type_doc.start_time else None
				shift_end_time = format_time(shift_type_doc.end_time, format_string="HH:mm") if shift_type_doc.end_time else None
		# Get employee checkins for this date
		checkins = frappe.get_all(
			"Employee Checkin",
			filters={
				"employee": employee,
				"time": ["between", [f"{date_str} 00:00:00", f"{date_str} 23:59:59"]]
			},
			fields=["log_type", "time", "device_id"],
			order_by="time asc"
		)
		
		# Process time logs and calculate clock in/out times
		time_logs = []
		clock_in_time = None
		unformatted_clock_in_time = None
		unformatted_clock_out_time = None
		clock_out_time = None
		clock_out_missing = False
		swipe_missing_in = False
		swipe_missing_out = False
		
		for checkin in checkins:
			time_logs.append({
				"log_type": checkin.log_type,
				"time": format_datetime(checkin.time, format_string="hh:mm a"),
				"missing": False
			})
			
			if checkin.log_type == "IN" and not clock_in_time:
				clock_in_time = format_datetime(checkin.time, format_string="hh:mm:ss")
				unformatted_clock_in_time = format_datetime(checkin.time, format_string="HH:mm:ss")
			elif checkin.log_type == "OUT":
				clock_out_time = format_datetime(checkin.time, format_string="hh:mm:ss")
				unformatted_clock_out_time = format_datetime(checkin.time, format_string="HH:mm:ss")
		
		# Check for missing swipes
		if attendance and attendance.status == "Present":
			if not clock_in_time:
				swipe_missing_in = True
			if not clock_out_time:
				swipe_missing_out = True
				clock_out_missing = True
				time_logs.append({
					"log_type": "OUT",
					"time": "OUT missing",
					"missing": True
				})
		
		# Calculate late entry and early exit
		late_entry = False
		late_minutes = 0
		early_exit = False
		
		if attendance:
			# late_entry = attendance.late_entry or False
			early_exit = attendance.early_exit or False
			
			if clock_in_time and shift_start_time: # TODO: handle this crap in a better way
				try:
					# Convert shift_start_time from string to time object if needed
					if isinstance(shift_start_time, str):
						# Try different time formats since '10:00' doesn't match '%H:%M:%S'
						try:
							shift_start_time = datetime.strptime(shift_start_time, "%H:%M").time()
						except ValueError:
							try:
								shift_start_time = datetime.strptime(shift_start_time, "%I:%M %p").time()
							except ValueError:
								shift_start_time = datetime.strptime(shift_start_time, "%H:%M:%S").time()
					
					shift_start_datetime = datetime.combine(current_date, shift_start_time)
					
					# Convert clock_in_time to datetime object
					try:
						# Try parsing with the format used in format_datetime above
						clock_in_datetime = datetime.strptime(f"{date_str} {unformatted_clock_in_time}", "%Y-%m-%d %H:%M:%S")
					except ValueError:
						# If that fails, try alternative format
						clock_in_datetime = datetime.strptime(f"{date_str} {unformatted_clock_in_time}", "%Y-%m-%d %I:%M:%S %p")
					# if date_str == "2025-07-24":
					if clock_in_datetime > shift_start_datetime:
						late_minutes = int((clock_in_datetime - shift_start_datetime).total_seconds() / 60)
					# if late_minutes is greater than 15, then set late_entry to True
					if late_minutes > 0:
						late_entry = True
					else:
						late_entry = False
				except (ValueError, TypeError) as e:
					print("Error calculating late minutes:", e)
					late_minutes = 0
		
		# Calculate working hours
		effective_hours = "0h 0m"
		gross_hours = "0h 0m"
		effective_hours = convert_hours_to_string(get_effective_hours(checkins))
		gross_hours = convert_hours_to_string(get_gross_hours(checkins))
		
		if attendance and attendance.working_hours:
			hours = int(attendance.working_hours)
			minutes = int((attendance.working_hours - hours) * 60)
			effective_hours = f"{hours}h {minutes}m"
			gross_hours = get_gross_hours(checkins)
			# format gross_hours to hh:mm
			gross_hours = convert_hours_to_string(gross_hours)
		
		# Determine penalties
		penalties = [] # TODO: add penalties implementations
		
		# Check for attendance regularization pending
		attendance_adjustment_pending = frappe.db.exists(
			"Attendance Regularization",
			{
				"employee": employee,
				"date": current_date,
				"docstatus": 0  # Draft status indicates pending
			}
		)
		attendance_adjustment_approved = frappe.db.exists(
			"Attendance Regularization",
			{
				"employee": employee,
				"date": current_date,
				"docstatus": 1  # Approved status indicates approved
			}
		)

		
		# Determine status
		status = "Absent"  # Default
		if attendance:
			if attendance.status == "On Leave":
				status = "Leave"
			elif attendance.status == "Half Day":
				status = "Half Day"
			elif attendance.status == "Present":
				status = "Present"
			elif attendance.status == "Work From Home":
				status = "Work From Home"
			else:
				status = attendance.status
		else:
			if holidays: # a dict of str:dict
				if date_str in holidays.keys():
					# find holiday with date_str in holidays
					holiday = holidays[date_str]
					if holiday["is_weekly_off"]:
						status = "Week Off"
					else:
						status = "Holiday"
		# if attendance.status if half day, then get the half day session from the leave application and manually calculate the gross and effective hours
		half_day_session = None
		if attendance and attendance.status == "Half Day":
			if_leave_application = frappe.db.exists(
				"Leave Application",
				{
					"employee": employee,
					"from_date": ["<=", current_date],
					"to_date": [">=", current_date],
					"status": ["in", ["Approved", "Open"]],
					"half_day": 1,
					"half_day_date": current_date,
					"docstatus": 1
				}
			)
			if if_leave_application:
				leave_application = frappe.get_doc("Leave Application", if_leave_application)
				if leave_application.status == "Approved":
					status = "Half Day"
					half_day_session = leave_application.custom_half_day_session
					gross_hours = convert_hours_to_string(get_gross_hours(checkins))
					effective_hours = convert_hours_to_string(get_effective_hours(checkins))
		# for higher priority of leaves (attendance may or may not be present), then get the leave application and check if the leave is approved
		if_leave_application = frappe.db.exists(
			"Leave Application",
			{
				"employee": employee,
				"from_date": ["<=", current_date],
				"to_date": [">=", current_date],
				"status": ["in", ["Approved", "Open"]],
				# "half_day": 1,
				# "half_day_date": current_date,
				"docstatus": ["in", [0, 1]]
			}
		)
		if if_leave_application:
			leave_application = frappe.get_doc("Leave Application", if_leave_application)
			if leave_application.status in ["Approved", "Open"]:
				if leave_application.half_day and leave_application.half_day_date == current_date:
					status = "Half Day"
					half_day_session = leave_application.custom_half_day_session
					gross_hours = convert_hours_to_string(get_gross_hours(checkins))
					effective_hours = convert_hours_to_string(get_effective_hours(checkins))
				else:
					status = "Leave"
					# leave_type = leave_application.leave_type
					# leave_days = leave_application.total_leave_days
					# leave_days_without_holidays = leave_application.total_leave_days_without_holidays
					# leave_days_with_holidays = leave_application.total_leave_days_with_holidays

		# Build the attendance record
		attendance_record = {
			"date": date_str,
			"status": status,
			"half_day_session": half_day_session,
			"shift_name": shift_name,
			"shift_start_time": format_time(shift_start_time,format_string="hh:mm a"),
			"shift_end_time": format_time(shift_end_time,format_string="hh:mm a"),
			"clock_in_time": format_time(unformatted_clock_in_time,format_string="hh:mm a") if unformatted_clock_in_time else unformatted_clock_in_time or clock_in_time,
			"clock_out_time": format_time(unformatted_clock_out_time,format_string="hh:mm a") if unformatted_clock_out_time else unformatted_clock_out_time or clock_out_time,
			"clock_out_missing": clock_out_missing,
			"late_entry": late_entry,
			"late_minutes": late_minutes,
			"early_exit": early_exit,
			"effective_hours": effective_hours,
			"gross_hours": gross_hours,
			"penalties": penalties,
			"attendance_adjustment_pending": bool(attendance_adjustment_pending),
			"attendance_adjusted": bool(attendance_adjustment_approved),
			"swipe_missing_in": swipe_missing_in,
			"swipe_missing_out": swipe_missing_out,
			"time_logs": time_logs
		}
		
		attendance_history.append(attendance_record)
		current_date = add_days(current_date, 1)
	
	return attendance_history

def convert_hours_to_string(hours: float | None) -> str:
	"""
	Convert hours to string
	hours: float or None
	"""
	if hours is None:
		return "0h 0m"
	hours_fixed = int(hours)
	minutes_fixed = int((hours - hours_fixed) * 60)
	return f"{hours_fixed}h {minutes_fixed}m"

@frappe.whitelist()
def get_gross_hours(checkins: list) -> float:
	"""
	Get gross and effective hours from checkins
	gross_hours = total time from first IN to last OUT
	"""
	total_hours = 0
	first_in_time = None
	last_out_time = None
	for checkin in checkins:
		if checkin.log_type == "IN":
			if not first_in_time:
				first_in_time = checkin.time
	for checkin in checkins[::-1]:
		if checkin.log_type == "OUT":
			if not last_out_time:
				last_out_time = checkin.time
	if first_in_time and last_out_time:
		total_hours = time_diff_in_hours(last_out_time, first_in_time)
	return total_hours

def get_effective_hours(checkins: list) -> float:
	"""
	Get effective hours from checkins
	effective_hours = sum of the pairs of IN and OUT
	"""
	effective_hours = 0
	for i in range(0, len(checkins)-1, 2):
		if checkins[i].log_type == "IN" and checkins[i+1].log_type == "OUT":
			effective_hours += time_diff_in_hours(checkins[i+1].time, checkins[i].time)
		else:
			effective_hours += time_diff_in_hours(checkins[i+1].time, checkins[i].time)
	
	return effective_hours

def get_holidays(employee: str,start_date: str, end_date: str) -> dict[str, dict]:
	"""
	Get holidays for an employee between start_date and end_date
	Args:
		employee (str): Employee ID
		shift_type (str): Shift type ID
		start_date (str): Start date in YYYY-MM-DD format
		end_date (str): End date in YYYY-MM-DD format
	Returns:
		list[dict]: List of holidays with date and description, is_weekly_off, is_holiday
	"""
	holiday_list = {}
	shift_assignment = frappe.db.sql("""
		SELECT shift_type, start_date, end_date
		FROM `tabShift Assignment`
		WHERE employee = %s 
			AND start_date <= %s 
			AND (end_date >= %s OR end_date IS NULL)
			AND docstatus = 1 
		ORDER BY start_date DESC
		LIMIT 1
	""", (employee, start_date, end_date), as_dict=True)
	shift_assignment = shift_assignment[0] if shift_assignment else None
	if shift_assignment:
		shift_type_doc = frappe.db.get_value(
			"Shift Type",
			shift_assignment.shift_type,
			["name", "start_time", "end_time"],
			as_dict=True
		)
		holiday_list = frappe.db.get_value("Shift Type", shift_type_doc.name, "holiday_list")
	
	if not holiday_list:
		holiday_list = frappe.db.get_value("Employee", employee, "holiday_list")
	holidays = frappe.get_all("Holiday", filters={"parent": holiday_list, "holiday_date": ("between", [start_date, end_date])}, fields=["holiday_date", "description", "weekly_off"])
	holidays = {holiday.holiday_date.strftime("%Y-%m-%d"): {"description": holiday.description, "is_weekly_off": holiday.weekly_off} for holiday in holidays}
	return holidays

@frappe.whitelist()
def get_employee_checkin_records(employee: str, date: str) -> list[dict]:
	"""
	Get employee checkin records for a specific date
	Args:
		employee (str): Employee ID
		date (str): Date in YYYY-MM-DD format
	Returns:
		list[dict]: List of checkin records with log_type, time, device_id
	"""
	from frappe.utils import getdate, format_datetime
	date_str = getdate(date).strftime("%Y-%m-%d")
	# get employee checkin records for the date
	checkins = frappe.get_all(
		"Employee Checkin",
		filters={
			"employee": employee,
			"time": ["between", [f"{date_str} 00:00:00", f"{date_str} 23:59:59"]]
		},
		fields=["log_type", "time", "device_id"],
		order_by="time asc"
	)
	checkins = [
		{
			"log_type": checkin.log_type,
			"time": format_datetime(checkin.time, format_string="hh:mm:ss"),
			"timestamp": checkin.time
		}
		for checkin in checkins
	]

	return checkins


@frappe.whitelist()
def get_attendance_regularization_requests(employee: str, filters: dict) -> list[dict]:
	"""
	Get attendance regularization requests for an employee
	Args:
		employee (str): Employee ID
		filters (dict): Filters for the attendance regularization requests (approver or employee)
	Returns:
		list[dict]: List of attendance regularization requests
	"""
	usable_filters = {}
	if filters.get("employee"):
		usable_filters["employee"] = filters["employee"]
	# when approver is provided, then get the employees under the approver
	if filters.get("approver"):
		employees = frappe.get_all(
			"Employee",
			filters={
				"user_id": ["!=", filters["approver"]]
			},
			or_filters=[
				{"reports_to": filters["approver"]},
				{"custom_reporting_manager_l1": filters["approver"]},
				{"custom_reporting_manager_l2": filters["approver"]},
				{"leave_approver": filters["approver"]}
			],
			fields=["name"]
		)
		employee_list = [e["name"] for e in employees]
		usable_filters["employee"] = ["in", employee_list]
	attendance_regularization_requests = frappe.get_all(
		"Attendance Regularization",
		filters=usable_filters,
		fields="*",
		limit=200
	)
	return attendance_regularization_requests
