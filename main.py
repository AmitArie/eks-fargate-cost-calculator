from collections import defaultdict
from dataclasses import dataclass
from kubernetes import client, config

namespace = "<YOUR_FARGATE_NAEMSAPCE_HERE>"

us_east_1_costs = {"vcpu": 0.04048, "memory": 0.004445, "storage": 0.000111}


@dataclass
class FargatePod:
    name: str
    app: str
    namesapce: str
    cpu: float
    memory: float


config.load_kube_config()

v1 = client.CoreV1Api()

fargate_pods = [
    FargatePod(
        name=pod.metadata.name,
        app=pod.metadata.labels["app"],
        namesapce=pod.metadata.namespace,
        cpu=float(
            pod.metadata.annotations["CapacityProvisioned"]
            .split()[0]
            .removesuffix("vCPU")
        ),
        memory=float(
            pod.metadata.annotations["CapacityProvisioned"]
            .split()[1]
            .removesuffix("GB")
        ),
    )
    for pod in v1.list_namespaced_pod(namespace=namespace).items
]


def calculate_price(fargate_pod: FargatePod):
    return (us_east_1_costs["vcpu"] * fargate_pod.cpu * 730) + (
        us_east_1_costs["memory"] * fargate_pod.memory * 730
    )


deployments_price = defaultdict(lambda: 0)
for fargate_pod in fargate_pods:
    deployments_price[fargate_pod.app] += calculate_price(fargate_pod)

print("service,price")
for svc, price in deployments_price.items():
    print(f"{svc},{price}$")
