import frappe
import requests

@frappe.whitelist(allow_guest=True)
def msg_send_otp(mobileNumber):
    api_url = frappe.conf.msg_api_url_send_otp
    auth_key = frappe.conf.msg_auth_key
    template_id = frappe.conf.msg_template_i
    payload = {
        "template_id": template_id,
        "mobile": f"91{mobileNumber}",
        "authkey": auth_key
    }
    response = requests.post(api_url, json=payload)
    return response

def msg_verify_otp(otp, mobileNumber):
    
    # Call the sendOTP API with the phone number
    api_url = frappe.conf.msg_api_url_verify_otp
    auth_key = frappe.conf.msg_auth_key
    headers = {
        "authkey": auth_key
    }
    params = {
        "mobile": mobileNumber,
        "otp": otp
    }
    response = requests.get(api_url,headers=headers, params=params)
    return response

