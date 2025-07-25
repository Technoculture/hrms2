import frappe
import json
from frappe import _
from frappe.utils import today, getdate

@frappe.whitelist()
def save_attendance_regularization(date, regularisation_reasonn, in_out_records, existing_checkins):
    from frappe.utils import getdate

    user = frappe.session.user
    employee = frappe.db.get_value("Employee", {"user_id": user}, "name")

    if not employee:
        frappe.throw("Employee not found for the current user.")

    # Parse list if passed as JSON string
    if isinstance(in_out_records, str):
        in_out_records = json.loads(in_out_records)

    doc = frappe.new_doc("Attendance Regularization")
    doc.update({
        "employee": employee,
        "date": getdate(date),
        "regularisation_reasonn": regularisation_reasonn,
        "custom_existing_checkins": existing_checkins,
    })

    for row in (in_out_records or []):
        doc.append("in_out_records", {
            "in_time":  "" if row.get("in_time") == None else row.get("in_time"),   # force blank
            "out_time": "" if row.get("out_time") == None else row.get("out_time"), # force blank
        })

    try:
        doc.insert(ignore_permissions=True)
    except Exception as e:
        import traceback
        print("Full traceback:")
        traceback.print_exc()
        return {
            "status": "error",
            "type": "validation",
            "message": str(e)  # ✅ Return the string version of the exception
        }

    return {
        "status": "success",
        "message": "Attendance Regularization submitted successfully.",
        "name": doc.name
    }

@frappe.whitelist()
def get_attendance_regularization_request(name: str) -> dict:
    """
    Get attendance regularization request by name
    """
    return frappe.get_doc("Attendance Regularization", name).as_dict()

@frappe.whitelist()
def submit_attendance_regularization(name: str, status: str) -> dict:
    """
    Submit attendance regularization request
    """
    doc = frappe.get_doc("Attendance Regularization", name)
    try:

        doc.submit()
    except Exception as e:
        print("error", e)
        return {
            "status": "error",
            "type": "validation",
            "message": str(e)  # ✅ Return the string version of the exception
        }
    return {
        "status": "success",
        "message": "Attendance Regularization submitted successfully.",
        "name": doc.name
    }