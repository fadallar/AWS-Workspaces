#!/usr/local/bin/python3
import boto3
import csv
import botocore
import argparse
from pprint import pprint
from tabulate import tabulate

def registerDomain(domainId,subnetList):
    """
    Check if a domain is already registered if not register it to Workspaces
    :Param String domainId - DomainId  to be registered
    :Param List subnetList - Pair of subnet used for association
    :Return True if domain succesfully registered False otherwise
    """
    try:
        if not isDomainRegistered(domainId):
            print("Registring Domain .......")
            client = boto3.client("workspaces")
            response = client.register_workspace_directory(
                DirectoryId= domainId,
                SubnetIds=[subnetList[0],subnetList[1]],
                EnableWorkDocs= False,
                EnableSelfService=False,
                Tenancy="SHARED"
            )
            if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
                return isDomainRegistered(domainId)
            else:
                print("Error registring domain {0}".format(domainId))
                return False
        else:
            print("Domain {0} already registered".format(domainId))
            return False
    except botocore.exceptions.ClientError as botoclient:
        print ("{0}".format(botoclient))
        return False
    except:
        print ("Undefined Error")
        return False

def isDomainRegistered(domainId):
    """
    Checks if a Domain is registered for Workspaces Services
    :Params Directory DomainId (string)
    :Return Boolean True: if Domain is registered: False Otherwise 
    """
    try:
        client = boto3.client("workspaces")
        response = client.describe_workspace_directories(
            DirectoryIds=[domainId]
            )
        for directory in response["Directories"]:
            if domainId == directory["DirectoryId"]:
                print("Domain registred with Registration Code {0}".format(directory["RegistrationCode"]))
                return True
        print("Domain {0} is not registered with Workspaces".format(domainId))
        return False
    except botocore.exceptions.ClientError as botoclient:
        print ("{0}".format(botoclient))
        return False
    except:
        print ("Undefined Error")
        return False

def verifyDomain(domainId):
    """
    Check if DomainId exists and is registered for Workspaces
    :Params Directory DomainId (string)
    :Return Boolean True: if Domain exists and is Registered False: Otherwise 
    """
    return checkDomainId(domainId) and isDomainRegistered(domainId)

def getDomainId(domainName):
    """
    :Params Directory Domain Name (String)
    :Return Directory Domain Id (String). None Otherwise
    """
    try:
        client = boto3.client("ds")
        response = client.describe_directories()
        for directory in response["DirectoryDescriptions"]:
            if directory["Name"] == domainName:
                return directory[""]
        return None
    except botocore.exceptions.ClientError as botoclient:
        print ("{0}".format(botoclient))
        return None
    except:
        print("Undefined Error")
        return None

def getWorkspacesList(Token=None):
    """
    :Return Directory Domain Id (String). None Otherwise
    """
    try:
        client = boto3.client('workspaces')
        paginator = client.get_paginator('describe_workspaces')
        response_iterator = paginator.paginate()
        WorkSpacesList = []
        for page in response_iterator:
            WorkSpacesList = WorkSpacesList + page["Workspaces"]
        return WorkSpacesList
    except botocore.exceptions.ClientError as botoclient:
        print ("{0}".format(botoclient))
        return None
    except:
        return None

def getDirectoriesList():
    """
    Return: List of Directories registered for Workspaces
    """
    try:
        client = boto3.client("workspaces")
        response = client.describe_workspace_directories()
        return response["Directories"]
    except botocore.exceptions.ClientError as botoclient:
        print ("{0}".format(botoclient))
        return None
    except:
        print("Undefined Error")
        return None

def getBundlesList():
    """
    To Do
    """
    try:
        client = boto3.client("workspaces")
        response = client.describe_workspace_bundles(Owner='AMAZON')
        return response["Bundles"]
    except botocore.exceptions.ClientError as botoclient:
        print ("{0}".format(botoclient))
        return None
    except:
        print("Undefined Error")
        return None

def checkBundleId(bundleId):
    """
    """
    try:
        client = boto3.client("workspaces")
        response = client.describe_workspace_bundles(BundleIds=[bundleId])
        for bundle in response["Bundles"]:
            if bundle["BundleId"] == bundleId:
                return bundle
        print("Can't find Bundle {0}".format(bundleId))
        return None
    except botocore.exceptions.ClientError as botoclient:
        print ("{0}".format(botoclient))
        return None
    except:
        print("Undefined Error")
        return None

def checkDomainId(domainId):
    """
    :Params Directory DomainId (string)
    :Return Boolean True: if Domain exists False: Otherwise 
    """
    try:
        client = boto3.client("ds")
        if client.describe_directories(DirectoryIds=[
        domainId]):
            return True
        else:
            print("Can't find domainId:{0}".format(domainId))
            return False
    except botocore.exceptions.ClientError as botoclient:
        print ("{0}".format(botoclient))
        return False
    except:
        print ("Undefined Error")
        return False

def createWorkspaces(workspacesList):
    """
    Create Workspaces based on a previously defined Workspaces List
    workspaces create_workspaces only accept max 25 Workspaces per call
    Hence the need of recursive call with batch of max 25 Workspaces.
    :Params WorkspacesList List of Dir
    """
    try:
        response = []
        client = boto3.client('workspaces')
        if len(workspacesList) <= 25:
            response.append(client.create_workspaces(Workspaces=workspacesList))
        else:
            response.append(client.create_workspaces(Workspaces=workspacesList[0:24]))
            newWorkspaceList = workspacesList[25:]
            response.append(createWorkspaces(newWorkspaceList))
        return response
    except botocore.exceptions.ClientError as botoclient:
        print ("{0}".format(botoclient))
        return None
    except :
        return None

def buildWorkSpacesList(userList,domainId,bundleId):
    """
    """
    workSpaces = []
    for user in userList:
        newWorkspace = {}
        newWorkspace["UserName"] = user["username"]
        newWorkspace["DirectoryId"] = domainId
        newWorkspace["BundleId"] = bundleId
        newWorkspace["UserVolumeEncryptionEnabled"] = False
        newWorkspace["RootVolumeEncryptionEnabled"] = False
        newWorkspace["WorkspaceProperties"] = {}
        newWorkspace["WorkspaceProperties"]["RunningMode"] = "AUTO_STOP"
        newWorkspace["WorkspaceProperties"]["RootVolumeSizeGib"] = 80
        newWorkspace["WorkspaceProperties"]["UserVolumeSizeGib"] = 10
        newWorkspace["WorkspaceProperties"]["ComputeTypeName"] = "VALUE"
        workSpaces.append(newWorkspace)
    return workSpaces

parser = argparse.ArgumentParser()
parser.add_argument("--userfilename", help="input user csv file name")
parser.add_argument("--domainId", help="directory domain id")
parser.add_argument("--bundleId", help="workspaces bundle id")
parser.add_argument("--registerdomainId",nargs='?', const="no", help="Flag yes or no - Register the provided DomainId with Workspaces")
parser.add_argument("--subnets", help="comma separated SubnetIds pair used for Domain Registration to Workspaces")
parser.add_argument("--action", help="Possible actions: ListWorkspaces, ListDirectories, ListBundles")
args = parser.parse_args()

userList = []
if args.action:
    if args.action == "ListWorkspaces":
        print (tabulate(getWorkspacesList(), headers="keys", tablefmt="psql"))
    elif args.action == "ListDirectories":
        pprint(getDirectoriesList())
    elif args.action == "ListBundles":
        print (tabulate(getBundlesList(), headers="keys", tablefmt="psql"))
elif args.registerdomainId and args.registerdomainId == "yes":
    subnetlist = args.subnets.split(",")
    if len(subnetlist) == 2 and checkDomainId(args.domainId):
        registerDomain(args.domainId,subnetlist)
    else:
        print("Please provide two comma separated subnetIds and a valid DomainId")
else:    
    if args.userfilename and args.domainId and args.bundleId:
        if verifyDomain(args.domainId) and checkBundleId(args.bundleId):
            try:
                with open(args.userfilename, newline='') as csvfile:
                    reader = csv.DictReader(csvfile)
                    for row in reader:
                        userList.append(row)
                pprint(createWorkspaces(buildWorkSpacesList(userList,args.domainId,args.bundleId)))
            except:
                raise
        else:
            print("Error: Please verify that DomainId and BundleId are correct")
    else:
        print("Error: Please provide all required arguments: userfilename,domainId and BundleId")