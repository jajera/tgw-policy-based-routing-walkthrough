---
layout: default
title: Reference
nav_order: 7
---

# Reference
{: .no_toc }

CLI commands and EC2 API actions for transit gateway policy tables — quick lookup for
scripts and troubleshooting.
{: .fs-5 .fw-300 }

## On this page
{: .no_toc .text-delta }

- TOC
{:toc}

---

## PBR operations

| Operation | AWS CLI Command | EC2 API Action | Documentation |
| --- | --- | --- | --- |
| Create policy table | `aws ec2 create-transit-gateway-policy-table` | `CreateTransitGatewayPolicyTable` | [API reference](https://docs.aws.amazon.com/AWSEC2/latest/APIReference/API_CreateTransitGatewayPolicyTable.html){:target="_blank"} |
| Delete policy table | `aws ec2 delete-transit-gateway-policy-table` | `DeleteTransitGatewayPolicyTable` | [API reference](https://docs.aws.amazon.com/AWSEC2/latest/APIReference/API_DeleteTransitGatewayPolicyTable.html){:target="_blank"} |
| Describe policy tables | `aws ec2 describe-transit-gateway-policy-tables` | `DescribeTransitGatewayPolicyTables` | [API reference](https://docs.aws.amazon.com/AWSEC2/latest/APIReference/API_DescribeTransitGatewayPolicyTables.html){:target="_blank"} |
| Associate policy table | `aws ec2 associate-transit-gateway-policy-table` | `AssociateTransitGatewayPolicyTable` | [API reference](https://docs.aws.amazon.com/AWSEC2/latest/APIReference/API_AssociateTransitGatewayPolicyTable.html){:target="_blank"} |
| Disassociate policy table | `aws ec2 disassociate-transit-gateway-policy-table` | `DisassociateTransitGatewayPolicyTable` | [API reference](https://docs.aws.amazon.com/AWSEC2/latest/APIReference/API_DisassociateTransitGatewayPolicyTable.html){:target="_blank"} |
| Get policy table entries | `aws ec2 get-transit-gateway-policy-table-entries` | `GetTransitGatewayPolicyTableEntries` | [API reference](https://docs.aws.amazon.com/AWSEC2/latest/APIReference/API_GetTransitGatewayPolicyTableEntries.html){:target="_blank"} |
| Get policy table associations | `aws ec2 get-transit-gateway-policy-table-associations` | `GetTransitGatewayPolicyTableAssociations` | [API reference](https://docs.aws.amazon.com/AWSEC2/latest/APIReference/API_GetTransitGatewayPolicyTableAssociations.html){:target="_blank"} |

{: .note }
> These API actions require appropriate IAM permissions. See the
> [Walkthrough](walkthrough) prerequisites for the minimum permission set.

## Further reading

For a complete guide to Transit Gateway policy tables including limits, quotas, and
feature updates, see the
[AWS Transit Gateway policy tables documentation](https://docs.aws.amazon.com/vpc/latest/tgw/tgw-policy-tables.html){:target="_blank"}.

[Next: Overview →]({{ site.baseurl }}/){: .btn .btn-primary .fs-5 .mb-4 .mb-md-0 }
