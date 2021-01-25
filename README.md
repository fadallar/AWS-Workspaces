# Amazon WorkSpaces Basic PoC Set-up

The following CloudFormation templates and scripts can be use to set-up a Proof of Concept Lab for Amazon Workspaces services.

The CloudFormation templates are used to set-up:

* A VPC with a set of subnets and Gateways (IGW and NAT Gateways)  
* A Managed Directory Service of your choice   ManagedAD or SimpleAD
* A Bastion Windows Server

A Powershell script is provided in order to bulk provision AD users
A Python script is provided in order to bulk provision Workspaces  

## Infrastructure Set-up

### VPC and Subnets

The Cloud formation template is provided [here](01-vpc-workspaces.yml)

Three set of subnets are created:

* Public subnets:
  * Two /24 subnets
  * Used by bastion hosts or public services
  * Associated with a route table with default route pointing to the Internet Gateway
* Workload subnets:
  * Two /21 subnnets
  * Used by the Workspaces
  * Associated with a route table with default route pointing to the NAT Gateway
* Managed Services subnets:
  * Two /24 subnets
  * Used by Managed Services such the directory services
  * Associated with a route table wich has no internet Access

All Subnets are automatically derived from the VPC CIDR Range which ideally should be a /16  

### Directory Services

Two Templates are provided, one for a [Managed AD](02a-managedAd.yml) and one for a [simple AD](02b-simpleAD.yml) set-up.
You  can choose one or the other  

### Windows Server Bastion

This [template](03-ec2-windowsServer.yml) is used to set-up a Windows Server 2019 Base server, to be used a Bastion Host and a Windows Management Server.
The template also creates Security group, Role, and Domain Auto-Join via a SSM Document.

> Important, you must create an EC2 SSH Key prior to launch this CloudFormation template  

The Windows AD Management Tools can be installed through Powershell

```PowerShell

Install-WindowsFeature RSAT-ADDS

```

If the Domain Auto-Join was not succesful you can join the domain manually using PowerShell  

```PowerShell

add-computer –domainname "YourDomainName"  -restart

```

## Supporting Scripts

### AD Users Creation

Simple Powershell scripts used to create AD USers in bulk.
It should be executed from the EC2 Bastion Host
Source is a csv file which should be dowloaded on the EC2 Instance
The script has two arguments, the path to the input csv file and the windows AD domain name.

```Bash

  createAdUsers.ps1 <inputCsvFile> <WindowsAdDomainName>

```

An example CSV file is provide in this Repo

### AWS Workspaces Creation

This is a python3  script which can be run from your Laptop

The script can be used for different tasks:

* Bulk provision Amazon Workspaces (!! Default Account Limit is 50 workspaces)
* Register a Domain with the Workspaces services
* List DomainIds, Workspaces and customer created Bundles

The Bulk workspace provisionning use the same CSV Input file as the PowerShell AD Script, currently the script will create all workspaces using the same provided BundleId.

```bash

python3 workspaces.py --userfilename <userCsvfile> --domainId <yourDomainId> --bundleId <yourBundleId>

```

> The workspaces  RootStorage, UserStorage and ComputeType are currently hard Coded

You can also register your Domain with the Workspaces Services using this Script. You will have to provide the DomainID and two comma separated subnetIds (must be in different AZ). These subnets are the workload Subnet created previously.

```bash

python3 workspaces.py  --domainId <yourDomainId> --registerdomainId yes --s <subnet-IdOne>,<subnetId-Two>

```

## To Dos, Gotchas, Bugs

[ ]: There is currently an issue with the EC2 Bastion Domain Auto-Join, which seems to be a bug with the AWS Provided SSM Document  
[ ]: Add support for Managed File System  
[ ]: Add support for WorkDocs Integration  
[ ]: Add Support for Directory Properties specific to Worspaces ( Local admin, HTTP Setup, IP Access Groups ...)  
[ ]: Add Capabilities to assign different BundleID per User in the CSV  
[ ]: Add Support for the python script to list Amazon provided Bundles  
[ ]: Add WorkSpaces Rollback features  
