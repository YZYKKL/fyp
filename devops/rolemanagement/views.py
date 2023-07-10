from django.shortcuts import render,redirect
from django.http import JsonResponse, QueryDict
from kubernetes import client, config
import os,hashlib,random
from devops import k8s
# Create your views here.

#@k8s.self_login_required
def role(request):
    return  render(request, 'rolemanagement/role.html')

#@k8s.self_login_required
def role_api(request):
    code = 0
    msg = ""
    auth_type = request.session.get("auth_type")
    token = request.session.get("token")
    k8s.load_auth_config(auth_type, token)
    api_client =client.ApiClient()
    # Create an instance of the API class
    api_instance = client.RbacAuthorizationV1Api(api_client)

    if request.method == "GET":
        search_key = request.GET.get("search_key")
        namespace = request.GET.get("namespace")
        data = []
        try:
            for role in api_instance.list_namespaced_role(namespace=namespace).items:  
                name = role.metadata.name
                namespace = role.metadata.namespace
                rules = []
                for rule in role.rules:
                    api_groups = rule.api_groups
                    resources = rule.resources
                    verbs = rule.verbs
                    rules.append({"api_groups":api_groups, "resources": resources, "verbs":verbs})
                role = {"name": name, "namespace": namespace, "rules":rules}
                print(role)
                if search_key:
                    if search_key in name:
                        data.append(role)
                else:
                    data.append(role)
                code = 0
                msg = "Fetch data successfully"
        except Exception as e:
            code = 1
            status = getattr(e, "status")
            if status == 403:
                msg = "Access denied!"
            else:
                msg = "Failed to fetch data"
        count = len(data)

        page = int(request.GET.get('page',1))
        limit = int(request.GET.get('limit'))
        start = (page - 1) * limit
        end = page * limit
        data = data[start:end]

        res = {'code': code, 'msg': msg, 'count': count, 'data': data}
        return JsonResponse(res)
    elif request.method == "DELETE":
        request_data = QueryDict(request.body)
        name = request_data.get("name")
        namespace = request_data.get("namespace")
        try:
            api_instance.delete_namespaced_role(namespace=namespace, name=name)
            code = 0
            msg = "Delete successfully."
        except Exception as e:
            code = 1
            status = getattr(e, "status")
            if status == 403:
                msg = "No delete permission!"
            else:
                msg = "Delete failed!"
        res = {'code': code, 'msg': msg}
        return JsonResponse(res)
    
@k8s.self_login_required
def role_bind(request):
    return render(request, 'rolemanagement/role_bind.html')

@k8s.self_login_required
def role_bind_api(request):
    code = 0
    msg = ""
    auth_type = request.session.get("auth_type")
    token = request.session.get("token")
    k8s.load_auth_config(auth_type, token)
    api_client = client.ApiClient()
    # Create an instance of the API class
    api_instance = client.RbacAuthorizationV1Api(api_client)

    if request.method == "GET":
        search_key = request.GET.get("search_key")
        namespace = request.GET.get("namespace")
        data = []
        try:
            for role_binding in api_instance.list_namespaced_role_binding(namespace=namespace).items:
                name = role_binding.metadata.name
                namespace = role_binding.metadata.namespace
                subjects = []
                role_ref = {}

                for subject in role_binding.subjects:
                    subject_kind = subject.kind
                    subject_name = subject.name
                    subject_api_group = subject.api_group
                    subject_namespace = subject.namespace
                    subjects.append({
                        "kind": subject_kind,
                        "name": subject_name,
                        "api_group": subject_api_group,
                        "namespace": subject_namespace
                    })

                role_ref_kind = role_binding.role_ref.kind
                role_ref_name = role_binding.role_ref.name
                role_ref_api_group = role_binding.role_ref.api_group
                role_ref = {
                    "kind": role_ref_kind,
                    "name": role_ref_name,
                    "api_group": role_ref_api_group
                }

                role_binding_data = {
                    "name": name,
                    "namespace": namespace,
                    "subjects": subjects,
                    "roleRef": role_ref
                }
                print(role_binding_data)
                if search_key:
                    if search_key in name:
                        data.append(role_binding_data)
                else:
                    data.append(role_binding_data)
                code = 0
                msg = "Fetch data successfully"
        except Exception as e:
            code = 1
            status = getattr(e, "status")
            if status == 403:
                msg = "Access denied!"
            else:
                msg = "Failed to fetch data"
        count = len(data)

        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit'))
        start = (page - 1) * limit
        end = page * limit
        data = data[start:end]

        res = {'code': code, 'msg': msg, 'count': count, 'data': data}
        return JsonResponse(res)
    elif request.method == "DELETE":
        request_data = QueryDict(request.body)
        name = request_data.get("name")
        namespace = request_data.get("namespace")
        try:
            api_instance.delete_namespaced_role_binding(namespace=namespace, name=name)
            code = 0
            msg = "Delete successfully."
        except Exception as e:
            code = 1
            status = getattr(e, "status")
            if status == 403:
                msg = "No delete permission!"
            else:
                msg = "Delete failed!"
        res = {'code': code, 'msg': msg}
        return JsonResponse(res)