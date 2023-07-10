from django.shortcuts import render, redirect
from django.http import JsonResponse, QueryDict
from kubernetes import client, config
import os,hashlib,random,yaml,json
from devops import k8s
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_exempt
from dashboard import node_data
# Create your views here.

@k8s.self_login_required
def index(request):
    return  render(request, 'index.html')

def login(request):
    if request.method == "GET":
        return  render(request, 'login.html')
    elif request.method == "POST":
        token = request.POST.get("token", None)

        if token:
            print(token)
            if k8s.auth_check('token', token):
                request.session['is_login'] = True
                request.session['auth_type'] = 'token'
                request.session['token'] = token
                code = 0
                msg = "Successful authentication"
            else:
                code = 1
                msg = "Token is invalid!"
        res = {'code': code, 'msg': msg}
        return JsonResponse(res)

@k8s.self_login_required
def logout(request):
    request.session.flush()
    return redirect(login)

@k8s.self_login_required
def namespace_api(request):
    if request.method == "GET":
        code = 0
        msg = ""
        auth_type = request.session.get("auth_type")
        token = request.session.get("token")
        k8s.load_auth_config(auth_type, token)
        core_api = client.CoreV1Api()
        search_key = request.GET.get("search_key")
        data = []
        try:
            for ns in core_api.list_namespace().items:
                name = ns.metadata.name
                labels = ns.metadata.labels
                create_time = ns.metadata.creation_timestamp
                namespace = {'name':name,'labels':labels,'create_time':create_time}
                
                if search_key:
                    if search_key in name:
                        data.append(namespace)
                else:
                    data.append(namespace)
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

        if request.GET.get('page'):
            page = int(request.GET.get('page',1))
            limit = int(request.GET.get('limit'))
            start = (page - 1) * limit
            end = page * limit
            data = data[start:end]

        res = {'code': code, 'msg': msg, 'count': count, 'data': data}
        print(res)
        return JsonResponse(res)

    elif request.method == "POST":
        name = request.POST['name']
        code = 0
        msg = ""
        auth_type = request.session.get("auth_type")
        token = request.session.get("token")
        k8s.load_auth_config(auth_type, token)
        core_api = client.CoreV1Api()
        search_key = request.GET.get("search_key")

        for ns in core_api.list_namespace().items:
            if name == ns.metadata.name:
                res = {'code': 1, "msg": "The namespace already exists!"}
                return JsonResponse(res)

        body = client.V1Namespace(
            api_version="v1",
            kind="Namespace",
            metadata=client.V1ObjectMeta(
                name=name
            )
        )
        try:
            core_api.create_namespace(body=body)
            code = 0
            msg = "Namespace created successfully."
        except Exception as e:
            code = 1
            status = getattr(e, "status")
            if status == 403:
                msg = "Access denied!"
            else:
                msg = "Creation failed!"
        res = {'code': code, 'msg': msg}
        return JsonResponse(res)

    elif request.method == "DELETE":
        request_data = QueryDict(request.body)
        name = request_data.get("name")
        auth_type = request.session.get("auth_type")
        token = request.session.get("token")
        k8s.load_auth_config(auth_type, token)
        core_api = client.CoreV1Api()
        try:
            core_api.delete_namespace(name)
            code = 0
            msg = "Delete successfully."
        except Exception as e:
            code = 1
            status = getattr(e, "status")
            if status == 403:
                msg = "No delete permission"
            else:
                msg = "Delete failed!"
        res = {'code': code, 'msg': msg}
        return JsonResponse(res)

@k8s.self_login_required
def namespace(request):
    return render(request, 'k8s/namespace.html')

@k8s.self_login_required
def create_resource(request):
    return  render(request, 'create_resource.html')

@k8s.self_login_required
def export_resource_api(request):
    auth_type = request.session.get("auth_type")
    token = request.session.get("token")
    k8s.load_auth_config(auth_type, token)
    core_api = client.CoreV1Api()  # namespace,pod,service,pv,pvc
    apps_api = client.AppsV1Api()  # deployment
    networking_api = client.NetworkingV1Api()  # ingress
    storage_api = client.StorageV1Api()  # storage_class
    api_client =client.ApiClient()
    Autoscaling_api = client.AutoscalingV1Api()
    # Create an instance of the API class
    api_instance = client.RbacAuthorizationV1Api(api_client)


    namespace = request.GET.get('namespace', None)
    resource = request.GET.get('resource', None)
    print(resource)
    name = request.GET.get('name', None)
    code = 0
    msg = ""
    result = ""

    import yaml,json
    if resource == "namespace":
        try:
            result = core_api.read_namespace(name=name, _preload_content=False).read()
            result = str(result, "utf-8")  # bytes转字符串
            result = yaml.safe_dump(json.loads(result))  # str/dict -> json -> yaml
        except Exception as e:
            code = 1
            msg = e
    elif resource == "deployment":
        try:
            result = apps_api.read_namespaced_deployment(name=name, namespace=namespace, _preload_content=False).read()
            result = str(result, "utf-8")
            result = yaml.safe_dump(json.loads(result))
        except Exception as e:
            code = 1
            msg = e
    elif resource == "replicaset":
        try:
            result = apps_api.read_namespaced_replica_set(name=name, namespace=namespace, _preload_content=False).read()
            result = str(result, "utf-8")
            result = yaml.safe_dump(json.loads(result))
        except Exception as e:
            code = 1
            msg = e
    elif resource == "daemonset":
        try:
            result = apps_api.read_namespaced_daemon_set(name=name, namespace=namespace, _preload_content=False).read()
            result = str(result, "utf-8")
            result = yaml.safe_dump(json.loads(result))
        except Exception as e:
            code = 1
            msg = e
    elif resource == "statefulset":
        try:
            result = apps_api.read_namespaced_stateful_set(name=name, namespace=namespace,
                                                           _preload_content=False).read()
            result = str(result, "utf-8")
            result = yaml.safe_dump(json.loads(result))
        except Exception as e:
            code = 1
            msg = e
    elif resource == "pod":
        try:
            result = core_api.read_namespaced_pod(name=name, namespace=namespace, _preload_content=False).read()
            result = str(result, "utf-8")
            result = yaml.safe_dump(json.loads(result))
        except Exception as e:
            code = 1
            msg = e
    elif resource == "service":
        try:
            result = core_api.read_namespaced_service(name=name, namespace=namespace, _preload_content=False).read()
            result = str(result, "utf-8")
            result = yaml.safe_dump(json.loads(result))
        except Exception as e:
            code = 1
            msg = e
    elif resource == "ingress":
        try:
            result = networking_api.read_namespaced_ingress(name=name, namespace=namespace,
                                                            _preload_content=False).read()
            result = str(result, "utf-8")
            result = yaml.safe_dump(json.loads(result))
        except Exception as e:
            code = 1
            msg = e
    elif resource == "pvc":
        try:
            result = core_api.read_namespaced_persistent_volume_claim(name=name, namespace=namespace,
                                                                      _preload_content=False).read()
            result = str(result, "utf-8")
            result = yaml.safe_dump(json.loads(result))
        except Exception as e:
            code = 1
            msg = e
    elif resource == "pv":
        try:
            result = core_api.read_persistent_volume(name=name, _preload_content=False).read()
            result = str(result, "utf-8")
            result = yaml.safe_dump(json.loads(result))
        except Exception as e:
            code = 1
            msg = e
    elif resource == "node":
        try:
            result = core_api.read_node(name=name, _preload_content=False).read()
            result = str(result, "utf-8")
            result = yaml.safe_dump(json.loads(result))
        except Exception as e:
            code = 1
            msg = e
    elif resource == "configmap":
        try:
            result = core_api.read_namespaced_config_map(name=name, namespace=namespace, _preload_content=False).read()
            result = str(result, "utf-8")
            result = yaml.safe_dump(json.loads(result))
        except Exception as e:
            code = 1
            msg = e
    elif resource == "secret":
        try:
            result = core_api.read_namespaced_secret(name=name, namespace=namespace, _preload_content=False).read()
            result = str(result, "utf-8")
            result = yaml.safe_dump(json.loads(result))
        except Exception as e:
            code = 1
            msg = e
    elif resource == "role":
        try:
            result = api_instance.read_namespaced_role(name=name, namespace=namespace, _preload_content=False).read()
            result = str(result, "utf-8")
            result = yaml.safe_dump(json.loads(result))
        except Exception as e:
            code = 1
            msg = e
    elif resource == "role_bind":
        try:
            result = api_instance.read_namespaced_role_binding(name=name, namespace=namespace, _preload_content=False).read()
            result = str(result, "utf-8")
            result = yaml.safe_dump(json.loads(result))
        except Exception as e:
            code = 1
            msg = e
    elif resource == "hpa":
        try:
            result = Autoscaling_api.read_namespaced_horizontal_pod_autoscaler(name=name, namespace=namespace, _preload_content=False).read()
            result = str(result, "utf-8")
            result = yaml.safe_dump(json.loads(result))
        except Exception as e:
            code = 1
            msg = e

    res = {"code": code, "msg": msg, "data": result}
    return JsonResponse(res)

@xframe_options_exempt
def ace_editor(request):
    d = {}
    namespace = request.GET.get('namespace', None)
    resource = request.GET.get('resource', None)
    name = request.GET.get('name', None)
    d['namespace'] = namespace
    d['resource'] = resource
    d['name'] = name
    return render(request, 'ace_editor.html', {'data': d})

@csrf_exempt
def upload_file(request):
    file_obj = request.FILES.get("file")
    random_str = hashlib.md5(str(random.random()).encode()).hexdigest()
    random_str = random_str + '.yaml'
    file_path = os.path.join('kubeconfig', random_str)
    try:
        with open(file_path, 'w', encoding='utf8') as f:
            data = file_obj.read().decode()  # bytes转str
            f.write(data)
            code = 0
            msg = file_path
    except Exception:
        code = 1
        msg = "File type error!"

    res = {"code": code, "msg": msg}
    return JsonResponse(res)

@csrf_exempt
def create_resource_api(request):
    auth_type = request.session.get("auth_type")
    token = request.session.get("token")
    k8s.load_auth_config(auth_type, token)
    core_api = client.CoreV1Api()  # namespace,pod,service,pv,pvc
    apps_api = client.AppsV1Api()  # deployment
    networking_api = client.NetworkingV1Api()  # ingress
    storage_api = client.StorageV1Api()  # storage_class
    api_client =client.ApiClient()
    Autoscaling_api = client.AutoscalingV1Api()
    # Create an instance of the API class
    api_instance = client.RbacAuthorizationV1Api(api_client)

    namespace = request.POST['namespace']
    resource = request.POST['resource']
    file_path = request.POST['path']

    print(namespace,resource,file_path)

    code = 0
    msg = ""

    import yaml,json
    if resource == "deployment":
        try:
            with open(file_path) as f:
                body = yaml.safe_load(f)
                apps_api.create_namespaced_deployment(namespace=namespace,body=body)
        except Exception as e:
            code = 1
            msg = "error"
    # elif resource == "replicaset":
    #     try:
    #         result = apps_api.read_namespaced_replica_set(name=name, namespace=namespace, _preload_content=False).read()
    #         result = str(result, "utf-8")
    #         result = yaml.safe_dump(json.loads(result))
    #     except Exception as e:
    #         code = 1
    #         msg = e
    elif resource == "daemonset":
        try:
            with open(file_path) as f:
                body = yaml.safe_load(f)
                apps_api.create_namespaced_daemon_set(namespace=namespace,body=body)
        except Exception as e:
            code = 1
            msg = "error"

    elif resource == "statefulset":
        try:
            with open(file_path) as f:
                body = yaml.safe_load(f)
                apps_api.create_namespaced_stateful_set(namespace=namespace,body=body)
        except Exception as e:
            code = 1
            msg = "error"
    elif resource == "pod":
        try:
            with open(file_path) as f:
                body = yaml.safe_load(f)
                core_api.create_namespaced_pod(namespace=namespace,body=body)
        except Exception as e:
            code = 1
            msg = "error"
    elif resource == "service":
        try:
            with open(file_path) as f:
                body = yaml.safe_load(f)
                core_api.create_namespaced_service(namespace=namespace,body=body)
        except Exception as e:
            code = 1
            msg = "error"
    elif resource == "ingress":
        try:
            with open(file_path) as f:
                body = yaml.safe_load(f)
                networking_api.create_namespaced_ingress(namespace=namespace,body=body)
        except Exception as e:
            code = 1
            msg = "error"
    elif resource == "pvc":
        try:
            with open(file_path) as f:
                body = yaml.safe_load(f)
                core_api.create_namespaced_persistent_volume_claim(namespace=namespace,body=body)
        except Exception as e:
            code = 1
            msg = "error"
    elif resource == "pv":
        try:
            with open(file_path) as f:
                body = yaml.safe_load(f)
                core_api.create_persistent_volume(body=body)
        except Exception as e:
            code = 1
            msg = "error"
    elif resource == "configmap":
        try:
            with open(file_path) as f:
                body = yaml.safe_load(f)
                core_api.create_namespaced_config_map(namespace=namespace,body=body)
        except Exception as e:
            code = 1
            msg = "error"
    elif resource == "secret":
        try:
            with open(file_path) as f:
                body = yaml.safe_load(f)
                core_api.create_namespaced_secret(namespace=namespace,body=body)
        except Exception as e:
            code = 1
            msg = "error"
    elif resource == "role":
        try:
            with open(file_path) as f:
                body = yaml.safe_load(f)
                api_instance.create_namespaced_role(namespace=namespace,body=body)
        except Exception as e:
            code = 1
            msg = "error"
    elif resource == "role_bind":
        try:
            with open(file_path) as f:
                body = yaml.safe_load(f)
                api_instance.create_namespaced_role_binding(namespace=namespace,body=body)
        except Exception as e:
            code = 1
            msg = "error"
    elif resource == "hpa":
        try:
            with open(file_path) as f:
                body = yaml.safe_load(f)
                Autoscaling_api.create_namespaced_horizontal_pod_autoscaler(namespace=namespace,body=body)
        except Exception as e:
            code = 1
            msg = "error"
            

    res = {"code": code, "msg": msg}
    return JsonResponse(res)

def node_resource(request):
    auth_type = request.session.get("auth_type")
    token = request.session.get("token")
    k8s.load_auth_config(auth_type, token)
    core_api = client.CoreV1Api()

    res = node_data.node_resource(core_api)
    return  JsonResponse(res)