variable "cloud_id" {
  description = "Yandex Cloud ID"
  type        = string
  default     = "b1ghfahdukhmskkq1sh"
}

variable "folder_id" {
  description = "Yandex Cloud Folder ID"
  type        = string
  default     = "b1goafhlbrpmfacul97b"
}

variable "zone" {
  description = "Yandex Cloud Zone"
  type        = string
  default     = "ru-central1-a"
}

variable "vm_name" {
  description = "Name of the virtual machine"
  type        = string
  default     = "terraform-vm"
}

variable "vm_cores" {
  description = "Number of CPU cores"
  type        = number
  default     = 2
}

variable "vm_memory" {
  description = "Amount of memory in GB"
  type        = number
  default     = 2
}

variable "vm_disk_size" {
  description = "Boot disk size in GB"
  type        = number
  default     = 10
}

variable "vm_image_id" {
  description = "OS image ID (Ubuntu 22.04)"
  type        = string
  default     = "fd8autg36kchufhej85b"
}

variable "ssh_public_key_path" {
  description = "Path to SSH public key"
  type        = string
  default     = "~/.ssh/id_rsa.pub"
}

variable "network_name" {
  description = "Name of the VPC network"
  type        = string
  default     = "network1"
}

variable "subnet_name" {
  description = "Name of the subnet"
  type        = string
  default     = "subnet1"
}

variable "subnet_cidr" {
  description = "CIDR block for subnet"
  type        = list(string)
  default     = ["192.168.10.0/24"]
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "project" {
  description = "Project name"
  type        = string
  default     = "devops-lab4"
}

variable "owner" {
  description = "Owner of the resources"
  type        = string
  default     = "angel-palkina"
}