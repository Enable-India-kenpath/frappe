import frappe

no_cache = 1


def get_context(context):
    print('=================')
    print(frappe.get_user().doc)
    context.username = frappe.get_user().doc
    if context.username != "Guest":
        userEmail = frappe.session.user
        user = frappe.get_all("User", filters={"email": userEmail}, fields=["name", "full_name", "email"])
        if user:
            context.userDetails = user[0]
            return context  # Return the first user found with the specified email
        else:
            return None
    return context