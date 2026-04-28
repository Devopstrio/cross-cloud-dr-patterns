provider "azurerm" {
  features {}
}

provider "aws" {
  region = var.aws_region
}

resource "azurerm_resource_group" "rg" {
  name     = "rg-${var.project_name}-${var.environment}"
  location = var.location
}

# Azure Kubernetes Cluster (Primary Region)
resource "azurerm_kubernetes_cluster" "primary" {
  name                = "aks-primary-${var.environment}"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  dns_prefix          = "dr-primary"

  default_node_pool {
    name       = "default"
    node_count = 3
    vm_size    = "Standard_DS3_v2"
  }

  identity {
    type = "SystemAssigned"
  }
}

# AWS EKS Cluster (Secondary Region - Failover Target)
module "eks_secondary" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 19.0"

  cluster_name    = "eks-secondary-${var.environment}"
  cluster_version = "1.27"

  vpc_id     = var.aws_vpc_id
  subnet_ids = var.aws_subnet_ids

  eks_managed_node_groups = {
    dr_nodes = {
      min_size     = 1
      max_size     = 5
      desired_size = 1 # Warm Standby
      instance_types = ["t3.medium"]
    }
  }
}

# Global Traffic Steering (Route53)
resource "aws_route53_record" "gslb" {
  zone_id = var.route53_zone_id
  name    = "app.${var.domain}"
  type    = "CNAME"
  ttl     = 60

  weighted_routing_policy {
    weight = 100
  }

  set_identifier = "primary-azure"
  records        = [azurerm_kubernetes_cluster.primary.fqdn]
}
