"""Pulumi program for Yandex Cloud VM infrastructure"""

import pulumi
import pulumi_yandex as yandex
import json

# Конфигурация
config = pulumi.Config()
cloud_id = config.get("cloud_id") or "b1ghfahdukhmskkq1sh"
folder_id = config.get("folder_id") or "b1goafhlbrpmfacul97b"
zone = config.get("zone") or "ru-central1-a"

# Читаем SSH ключ
with open("C:/Users/sofia/.ssh/id_rsa.pub", "r") as f:
    ssh_key = f.read().strip()

# Cloud-init конфигурация для пользователя
user_data = f"""#cloud-config
users:
  - name: ubuntu
    groups: sudo
    shell: /bin/bash
    sudo: ['ALL=(ALL) NOPASSWD:ALL']
    ssh-authorized-keys:
      - {ssh_key}
"""

# Создаем VPC сеть
network = yandex.VpcNetwork("network-1",
    name="pulumi-network",
    labels={
        "environment": "dev",
        "project": "devops-lab4",
        "owner": "angel-palkina",
        "managed_by": "pulumi"
    }
)

# Создаем подсеть
subnet = yandex.VpcSubnet("subnet-1",
    name="pulumi-subnet",
    zone=zone,
    network_id=network.id,
    v4_cidr_blocks=["192.168.20.0/24"],
    labels={
        "environment": "dev",
        "project": "devops-lab4",
        "owner": "angel-palkina",
        "managed_by": "pulumi"
    }
)

# Создаем виртуальную машину
vm = yandex.ComputeInstance("vm-1",
    name="pulumi-vm",
    platform_id="standard-v2",
    zone=zone,
    resources=yandex.ComputeInstanceResourcesArgs(
        cores=2,
        memory=2,
    ),
    boot_disk=yandex.ComputeInstanceBootDiskArgs(
        initialize_params=yandex.ComputeInstanceBootDiskInitializeParamsArgs(
            image_id="fd8autg36kchufhej85b",  # Ubuntu 22.04
            size=10,
        ),
    ),
    network_interfaces=[yandex.ComputeInstanceNetworkInterfaceArgs(
        subnet_id=subnet.id,
        nat=True,
    )],
    metadata={
        "user-data": user_data
    },
    labels={
        "environment": "dev",
        "project": "devops-lab4",
        "owner": "angel-palkina",
        "managed_by": "pulumi"
    }
)

# Outputs
pulumi.export("vm_id", vm.id)
pulumi.export("vm_name", vm.name)
pulumi.export("vm_external_ip", vm.network_interfaces[0].nat_ip_address)
pulumi.export("vm_internal_ip", vm.network_interfaces[0].ip_address)
pulumi.export("network_id", network.id)
pulumi.export("subnet_id", subnet.id)