# Ansible Automation

[![Ansible Deployment](https://github.com/angel-palkina/DevOps-Core-Course/actions/workflows/ansible-deploy.yml/badge.svg)](https://github.com/angel-palkina/DevOps-Core-Course/actions/workflows/ansible-deploy.yml)

## Lab 06 - Advanced Ansible & CI/CD

Automated deployment with GitHub Actions.

### Quick Start

```bash
# Deploy application
ansible-playbook playbooks/deploy.yml --ask-vault-pass

# Provision servers
ansible-playbook playbooks/provision.yml --ask-vault-pass

# Clean reinstall
ansible-playbook playbooks/deploy.yml -e "web_app_wipe=true" --ask-vault-pass