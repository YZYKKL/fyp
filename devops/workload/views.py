from django.shortcuts import render, redirect
from django.http import JsonResponse, QueryDict
from kubernetes import client, config
import os,hashlib,random
from devops import k8s
# Create your views here.

# Create your views here.

@k8s.self_login_required
def deployment(request):
    return  render(request, 'workload/deployment.html')

@k8s.self_login_required
def deployment_create(request):
    return  render(request, 'workload/deployment_create.html')

@k8s.self_login_required
def deployment_api(request):
    code = 0
    msg = ""
    auth_type = request.session.get("auth_type")
    token = request.session.get("token")
    k8s.load_auth_config(auth_type, token)
    apps_api = client.AppsV1Api()
    if request.method == "GET":
        search_key = request.GET.get("search_key")
        namespace = request.GET.get("namespace")
        data = []
        try:
            for dp in apps_api.list_namespaced_deployment(namespace=namespace).items:
                name = dp.metadata.name
                namespace = dp.metadata.namespace
                replicas = dp.spec.replicas
                available_replicas = ( 0 if dp.status.available_replicas is None else dp.status.available_replicas)
                labels = dp.metadata.labels
                selector = dp.spec.selector.match_labels
                if len(dp.spec.template.spec.containers) > 1:
                    images = ""
                    n = 1
                    for c in dp.spec.template.spec.containers:
                        status = ("Runing" if dp.status.conditions[0].status == "True" else "Exception")
                        image = c.image
                        images += "[%s]: %s / %s" % (n, image, status)
                        images += "<br>"
                        n += 1
                else:
                    status = (
                        "Runing" if dp.status.conditions[0].status == "True" else "Exception")
                    image = dp.spec.template.spec.containers[0].image
                    images = "%s / %s" % (image, status)

                create_time = dp.metadata.creation_timestamp
                dp = {"name": name, "namespace": namespace, "replicas":replicas,
                             "available_replicas":available_replicas , "labels":labels, "selector":selector,
                             "images":images, "create_time": create_time}
                
                if search_key:
                    if search_key in name:
                        data.append(dp)
                else:
                    data.append(dp)
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
    
    elif request.method == "PUT":
        request_data = QueryDict(request.body)
        name = request_data.get("name")
        namespace = request_data.get("namespace")
        replicas = int(request_data.get("replicas"))
        try:
            body = apps_api.read_namespaced_deployment(name=name, namespace=namespace)
            current_replicas = body.spec.replicas
            min_replicas = 0
            max_replicas = 10
            if replicas > current_replicas and replicas < max_replicas:
                body.spec.replicas = replicas
                apps_api.patch_namespaced_deployment(name=name, namespace=namespace, body=body)
                msg = "Successful scale in!"
                code = 0
            elif replicas < current_replicas and replicas > min_replicas:
                body.spec.replicas = replicas
                apps_api.patch_namespaced_deployment(name=name, namespace=namespace, body=body)
                msg = "Successful scale out!"
                code = 0
            elif replicas == current_replicas:
                msg = "Replicas no change"
                code = 1
            elif replicas > max_replicas:
                msg = "Set the number of Replicas too large!"
                code = 1
            elif replicas == min_replicas:
                msg = "The number of Replicas cannot be set to 0!"
                code = 1
        except Exception as e:
            status = getattr(e, "status")
            if status == 403:
                msg = "No Permissions!"
            else:
                msg = "Scaling failure!"
            code = 1
        res = {"code": code, "msg": msg}
        return JsonResponse(res)

    elif request.method == "DELETE":
        request_data = QueryDict(request.body)
        name = request_data.get("name")
        namespace = request_data.get("namespace")
        try:
            apps_api.delete_namespaced_deployment(namespace=namespace, name=name)
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
def daemonset(request):
    return  render(request, 'workload/daemonset.html')

@k8s.self_login_required
def daemonset_api(request):
    code = 0
    msg = ""
    auth_type = request.session.get("auth_type")
    token = request.session.get("token")
    k8s.load_auth_config(auth_type, token)
    apps_api = client.AppsV1Api()
    if request.method == "GET":
        search_key = request.GET.get("search_key")
        namespace = request.GET.get("namespace")
        data = []
        try:
            for ds in apps_api.list_namespaced_daemon_set(namespace).items:
                name = ds.metadata.name
                namespace = ds.metadata.namespace
                desired_number = ds.status.desired_number_scheduled
                available_number = ds.status.number_available
                labels = ds.metadata.labels
                selector = ds.spec.selector.match_labels
                containers = {}
                for c in ds.spec.template.spec.containers:
                    containers[c.name] = c.image
                create_time = ds.metadata.creation_timestamp

                ds = {"name": name, "namespace": namespace, "labels": labels, "desired_number": desired_number,
                      "available_number": available_number,
                      "selector": selector, "containers": containers, "create_time": create_time}

                
                if search_key:
                    if search_key in name:
                        data.append(ds)
                else:
                    data.append(ds)
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
            apps_api.delete_namespaced_daemon_set(namespace=namespace, name=name)
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
def statefulset(request):
    return  render(request, 'workload/statefulset.html')

@k8s.self_login_required
def statefulset_api(request):
    code = 0
    msg = ""
    auth_type = request.session.get("auth_type")
    token = request.session.get("token")
    k8s.load_auth_config(auth_type, token)
    apps_api = client.AppsV1Api()
    if request.method == "GET":
        search_key = request.GET.get("search_key")
        namespace = request.GET.get("namespace")
        data = []
        try:
            for sts in apps_api.list_namespaced_stateful_set(namespace).items:
                name = sts.metadata.name
                namespace = sts.metadata.namespace
                labels = sts.metadata.labels
                selector = sts.spec.selector.match_labels
                replicas = sts.spec.replicas
                ready_replicas = ("0" if sts.status.ready_replicas is None else sts.status.ready_replicas)
                # current_replicas = sts.status.current_replicas
                service_name = sts.spec.service_name
                containers = {}
                for c in sts.spec.template.spec.containers:
                    containers[c.name] = c.image
                create_time = sts.metadata.creation_timestamp

                sts = {"name": name, "namespace": namespace, "labels": labels, "replicas": replicas,
                      "ready_replicas": ready_replicas, "service_name": service_name,
                      "selector": selector, "containers": containers, "create_time": create_time}

                # 根据搜索值返回数据
                if search_key:
                    if search_key in name:
                        data.append(sts)
                else:
                    data.append(sts)
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
            apps_api.delete_namespaced_stateful_set(namespace=namespace, name=name)
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
def pod(request):
    return  render(request, 'workload/pod.html')

@k8s.self_login_required
def pod_api(request):
    code = 0
    msg = ""
    auth_type = request.session.get("auth_type")
    token = request.session.get("token")
    k8s.load_auth_config(auth_type, token)
    core_api = client.CoreV1Api()
    if request.method == "GET":
        search_key = request.GET.get("search_key")
        namespace = request.GET.get("namespace")
        data = []
        try:
            for po in core_api.list_namespaced_pod(namespace).items:
                name = po.metadata.name
                namespace = po.metadata.namespace
                labels = po.metadata.labels
                pod_ip = po.status.pod_ip

                containers = [] 
                status = "None"

                if po.status.container_statuses is None:
                    status = po.status.conditions[-1].reason
                else:
                    for c in po.status.container_statuses:
                        c_name = c.name
                        c_image = c.image

                        
                        restart_count = c.restart_count

                        
                        c_status = "None"
                        if c.ready is True:
                            c_status = "Running"
                        elif c.ready is False:
                            if c.state.waiting is not None:
                                c_status = c.state.waiting.reason
                            elif c.state.terminated is not None:
                                c_status = c.state.terminated.reason
                            elif c.state.last_state.terminated is not None:
                                c_status = c.last_state.terminated.reason

                        c = {'c_name': c_name, 'c_image': c_image, 'restart_count': restart_count, 'c_status': c_status}
                        containers.append(c)

                create_time = po.metadata.creation_timestamp

                po = {"name": name, "namespace": namespace, "pod_ip": pod_ip,
                      "labels": labels, "containers": containers, "status": status,
                      "create_time": create_time}

                
                if search_key:
                    if search_key in name:
                        data.append(po)
                else:
                    data.append(po)
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
            core_api.delete_namespaced_pod(namespace=namespace, name=name)
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
def pod_log(request):
    auth_type = request.session.get("auth_type")
    token = request.session.get("token")
    k8s.load_auth_config(auth_type, token)
    core_api = client.CoreV1Api()

    name = request.POST.get("name", None)
    namespace = request.POST.get("namespace", None)

    try:
        log_text = core_api.read_namespaced_pod_log(name=name, namespace=namespace, tail_lines=500)
        if log_text:
            code = 0
            msg = "Log fetching success!"
        elif len(log_text) == 0:
            code = 0
            msg = "No logs!"
            log_text = "No logs!"
    except Exception as e:
        status = getattr(e, "status")
        if status == 403:
            msg = "You don't have access to logs!"
        else:
            msg = "Log fetching failed!"
        code = 1
        log_text = "Log fetching failed!"
    res = {"code": code, "msg": msg, "data": log_text}
    return JsonResponse(res)



@k8s.self_login_required
def hpa(request):
    return  render(request, 'workload/hpa.html')

@k8s.self_login_required
def hpa_api(request):
    code = 0
    msg = ""
    auth_type = request.session.get("auth_type")
    token = request.session.get("token")
    k8s.load_auth_config(auth_type, token)
    core_api = client.CoreV1Api()
    api_instance = client.AutoscalingV1Api()
    if request.method == "GET":
        search_key = request.GET.get("search_key")
        namespace = request.GET.get("namespace")
        
        data = []
        try:
            for hpa in api_instance.list_namespaced_horizontal_pod_autoscaler(namespace).items:
                print(hpa)
                name = hpa.metadata.name
                namespace = hpa.metadata.namespace
                ref = hpa.spec.scale_target_ref
                target1 = hpa.status.current_cpu_utilization_percentage
                target2 = hpa.spec.target_cpu_utilization_percentage
                min_pods = hpa.spec.min_replicas
                max_pods = hpa.spec.max_replicas
                replicas = hpa.status.current_replicas
                create_time = hpa.metadata.creation_timestamp.strftime("%Y-%m-%d %H:%M:%S")
                
                hpa_data = {
                    "name": name,
                    "namespace": namespace,
                    "reference": f"{ref.kind}/{ref.name}",
                    "targets": f"{target1}%/{target2}%",
                    "min_pods": min_pods,
                    "max_pods": max_pods,
                    "replicas": replicas,
                    "create_time": create_time
                }
                print(hpa_data)
                if search_key:
                    if search_key in name:
                        data.append(hpa_data)
                else:
                    data.append(hpa_data)
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
            api_instance.delete_namespaced_horizontal_pod_autoscaler(namespace=namespace, name=name)
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