resource "yandex_compute_instance" "vm-1" {
  name        = var.vm_name
  platform_id = "standard-v2"
  zone        = var.zone

  labels = {
    environment = var.environment
    project     = var.project
    owner       = var.owner
    managed_by  = "terraform"
  }

  resources {
    cores  = var.vm_cores
    memory = var.vm_memory
  }

  boot_disk {
    initialize_params {
      image_id = var.vm_image_id
      size     = var.vm_disk_size
    }
  }

  network_interface {
    subnet_id = yandex_vpc_subnet.subnet-1.id
    nat       = true
  }

  metadata = {
    user-data = <<-EOT
      #cloud-config
      users:
        - name: ubuntu
          groups: sudo
          shell: /bin/bash
          sudo: ['ALL=(ALL) NOPASSWD:ALL']
          ssh-authorized-keys:
            - ${file(pathexpand(var.ssh_public_key_path))}
    EOT
  }
}

resource "yandex_vpc_network" "network-1" {
  name = var.network_name

  labels = {
    environment = var.environment
    project     = var.project
    owner       = var.owner
    managed_by  = "terraform"
  }
}

resource "yandex_vpc_subnet" "subnet-1" {
  name           = var.subnet_name
  zone           = var.zone
  network_id     = yandex_vpc_network.network-1.id
  v4_cidr_blocks = var.subnet_cidr

  labels = {
    environment = var.environment
    project     = var.project
    owner       = var.owner
    managed_by  = "terraform"
  }
}