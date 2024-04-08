import frappe

no_cache = 1


def get_context(context):
	print(frappe.session.user)
	if frappe.session.user != "Guest":
		user_role = frappe.get_roles(username=frappe.session.user)
		user_doc = frappe.get_doc("User", frappe.session.user)
		user_type = user_doc.user_type
		print(user_type)
		if  'Administrator' not in user_role or "System Manager" not in user_role:
			roles_tuple = user_role[0]
		else:
			roles_tuple = tuple(user_role)
		doc_list = get_doc_type_list_role(roles_tuple)
		list = []
		if len(doc_list) > 0:
			for doc in doc_list:
				parent_value = doc.get('parent')
				doc_list_query = """SELECT name as Registry_Type, modified_by as Modified_By, module as Module FROM kenpathErp.tabDocType where kenpathErp.tabDocType.name = %r""" %(parent_value)
				doc_list_result = frappe.db.sql(doc_list_query, as_dict=True)
				list.append(doc_list_result)
				context.doc_type_list = list
			return context
		else:
			context.doc_type_list = []
			return context

def get_doc_type_list_role(role):
	if isinstance(role, str):
		doc_list_role_query = """SELECT parent, role from kenpathErp.tabDocPerm where role = %r""" % (role)
	else:	
		doc_list_role_query = """SELECT parent, role from kenpathErp.tabDocPerm where role IN %r""" % (role,)
	doc_Types = frappe.db.sql(doc_list_role_query, as_dict=True)
	return doc_Types
