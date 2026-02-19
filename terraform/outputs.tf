output "vm_external_ip" {
  description = "External IP address of the VM"
  value       = yandex_compute_instance.vm-1.network_interface[0].nat_ip_address
}

output "vm_internal_ip" {
  description = "Internal IP address of the VM"
  value       = yandex_compute_instance.vm-1.network_interface[0].ip_address
}

output "vm_id" {
  description = "ID of the VM"
  value       = yandex_compute_instance.vm-1.id
}