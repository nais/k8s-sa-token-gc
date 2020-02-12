#!/usr/bin/env python3
import urllib3
from kubernetes import client, config
from kubernetes.client.rest import ApiException

urllib3.disable_warnings()

config.load_kube_config()
api = client.CoreV1Api()
pods = api.list_pod_for_all_namespaces()

in_use_tokens = []
for pod in pods.items:
    for vol in pod.spec.volumes:
        if 'token' in vol.name and vol.secret:
            in_use_tokens.append(vol.secret.secret_name)

service_accounts = api.list_service_account_for_all_namespaces()
for sa in service_accounts.items:
    for token in sa.secrets:
        in_use_tokens.append(token.name)

namespaces = api.list_namespace()
for ns in namespaces.items:
    secrets = api.list_namespaced_secret(ns.metadata.name,
                                         field_selector='type=kubernetes.io/service-account-token',
                                         timeout_seconds=25 * 60)
    for secret in secrets.items:
        if secret.metadata.name not in in_use_tokens and 'default' not in secret.metadata.name \
                and secret.metadata.namespace != 'kube-system':
            try:
                print('deleting', secret.metadata.namespace, secret.metadata.name)
                # api.delete_namespaced_secret(secret.metadata.name, secret.metadata.namespace)
            except ApiException as e:
                print('exception while deleting: ', e)
