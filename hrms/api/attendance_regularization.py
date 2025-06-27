import frappe
import json
from frappe import _
from frappe.utils import today

@frappe.whitelist()
def submit_attendance_regularization(date, regularisation_reasonn, in_out_records):
    from frappe.utils import getdate

    user = frappe.session.user
    employee = frappe.db.get_value("Employee", {"user_id": user}, "name")

    if not employee:
        frappe.throw("Employee not found for the current user.")

    # Parse list if passed as JSON string
    if isinstance(in_out_records, str):
        in_out_records = json.loads(in_out_records)

    doc = frappe.get_doc({
        "doctype": "Attendance Regularization",
        "employee": employee,
        "date": getdate(date),
        "regularisation_reasonn": regularisation_reasonn,
        "in_out_records": in_out_records
    })

    doc.insert(ignore_permissions=True)

    return {
        "status": "success",
        "message": "Attendance Regularization submitted successfully.",
        "name": doc.name
    }