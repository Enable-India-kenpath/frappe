import frappe
import json
from urllib.parse import urlparse, parse_qs
import psycopg2
frappe.utils.logger.set_log_level("INFO")
logger = frappe.logger("api", allow_site=True, file_count=50)
from datetime import datetime

no_cache = 1


def get_context(context):
    username = frappe.get_user().doc
    context.sessionDetails = {
        "noOfSessionsAttempted": "--",
        "noOfBlimeyExercisesAttempted":"--",
        "noOfLivelihoodOpprtunities":"--",
        "noOfEnterpreneur":"--",
        "skillBasedOpportunities":"--",
        "lastUpdatedOn":datetime.now().date()
    }

    context.isBlimeyEnabled = True
    context.isVaaniEnabled = True
    current_url = frappe.local.request.url
    query_params = get_query_params(current_url)
    userId = None
    if query_params:
        userId = query_params['id'][0]
    if userId :
        print(userId)
        docTypeData = frappe.get_all("PWD Profile", fields=["first_name", "email", "phone_number", "photo"], filters={"name":userId}, limit=10)
        userPhoneNumber = docTypeData[0]['phone_number']
        print(docTypeData)
        # vaaniDetails = get_user_data(userPhoneNumber, context)
        # user = frappe.get_all("User", filters={"email": userEmail}, fields=["name", "full_name", "email"])
        if docTypeData:
            userDetails = {
                "full_name": docTypeData[0]['first_name'] + ' ',
                "photo" : docTypeData[0]['photo']
            }
            context.userDetails = userDetails
        else:
            context.userDetails = None
        return context

    # Get Doctype data
    elif username != "Guest":
        userEmail = username.email
        docTypeData = frappe.get_all("PWD Profile", fields=['*'], filters={"email":userEmail}, limit=10)
        user = frappe.get_all("User", filters={"email": userEmail}, fields=["name", "full_name", "email"])
        if user:
            context.userDetails = user[0]
        else:
            context.userDetails = None
    return context

@frappe.whitelist(allow_guest=True)
def submit():
    try : 
        # Access form fields from the metadata
        form_data = json.loads(frappe.form_dict.get("form_data"))
        existing_doc = frappe.get_all("PWD Profile", filters={"email": form_data.get("email")}, limit=1)
        if existing_doc:
            # Save each key-value pair to the database
            doc = frappe.get_doc("PWD Profile",existing_doc[0].name)
            for key, value in form_data.items():
                doc.set(key, value)
            doc.save(ignore_permissions=True)
            updateUser = update_user_data(form_data['email'], form_data)
            if updateUser:
                frappe.msgprint("Document Updated Successfully")
                return  {"message": "Record updated successfully.", "status":True}
        else:
            for key, value in form_data.items():
                    print(key)
                    # Save each key-value pair to the database
                    doc = frappe.get_doc({
                        "doctype": "PWD Profile",
                        key: value,
                    })
                    # doc.insert(ignore_permissions=True)
                    # doc.save()
        # Redirect to a success page or render a success message
    except Exception as e:
        return frappe.utils.error.collect_error_snapshots()
    
def update_user_data(email, formData):
    user = frappe.get_all("User", filters={"email": email}, limit=1)
    print(user)
    if user:
        user_doc = frappe.get_doc("User", user[0].name)
        user_doc.update({
            "first_name": formData.get("name1"),
        })
        user_doc.save(ignore_permissions = True)
    return True
def get_query_params(url):
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    return query_params

def get_user_data(phoneNumber, context):
    print(phoneNumber)
    phoneNumberWithoutCode = phoneNumber[4:]
    print(phoneNumberWithoutCode)
    conn = psycopg2.connect(database = frappe.conf.postgres_db,
                            user = frappe.conf.postgres_user,
                            host= frappe.conf.postgres_host,
                            password = frappe.conf.postgres_password,
                            port = frappe.conf.postgres_port)

    cur = conn.cursor()
    query = """select mobile_number, is_blimey_tool_used, is_enable_vaani_used from public.ei_user_data where mobile_number=%r""" %phoneNumberWithoutCode
    cur.execute(query)
    ei_user_data = cur.fetchone()
    if ei_user_data[2]:
        query = "SELECT contributor AS contributor, count(DISTINCT audio_url) AS Number of Calls, AVG(duration) AS Average Duration FROM public.dim_items where contributor='91" + phoneNumberWithoutCode + "' GROUP BY contributor ORDER BY Number of Calls DESC LIMIT 20;"
        cur.execute(query)

    rows = cur.fetchall()
    for row in rows:
        context.vaaniDetails = {
            "contributor" : row[0],
            "noOfCalls" : row[1],
            "average" : row[2]
        }
        print(row)

    conn.close()
    return rows