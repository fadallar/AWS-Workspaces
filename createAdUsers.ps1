# Defining CLI parameters
param([string] $inputfileName, 
      [string] $domainName)

# Import active directory module for running AD cmdlets
Import-Module ActiveDirectory
  
# Store the data from the input CSV file in the $ADUsers variable
$ADUsers = Import-Csv $inputfileName ","

# Define UPN
$UPN = $domainName

# Loop through each row containing user details in the CSV file
foreach ($User in $ADUsers) {
    #Read user data from each field in each row and assign the data to a variable as below
    $username = $User.username
    $password = $User.password
    $firstname = $User.firstname
    $lastname = $User.lastname
    $initials = $User.initials
    #$OU = "OU=Users,OU=ad,DC=ad,DC=indbertrix,DC=be"#This field refers to the OU the user account is to be created in
    #$email = $User.email
    #$streetaddress = $User.streetaddress
    #$city = $User.city
    #$zipcode = $User.zipcode
    #$state = $User.state
    #$telephone = $User.telephone
    #$jobtitle = $User.jobtitle
    #$company = $User.company
    #$department = $User.department

    # Check to see if the user already exists in AD
    if (Get-ADUser -F { SamAccountName -eq $username }) {
        
        # If user does exist, give a warning
        Write-Warning "A user account with username $username already exists in Active Directory."
    }
    else {

        # User does not exist then proceed to create the new user account
        # Account will be created in the OU provided by the $OU variable read from the CSV file
        New-ADUser `
        -SamAccountName $username `
        -UserPrincipalName "$username@$UPN" `
        -Name "$username" `
        -GivenName $firstname `
        -Surname $lastname `
        -Initials $initials `
        -Enabled $True `
        -DisplayName "$lastname, $firstname" `
        -AccountPassword (ConvertTo-secureString $password -AsPlainText -Force) -ChangePasswordAtLogon $False `
        #-Path $OU `
            #-City $city `
            #-PostalCode $zipcode `
            #-Company $company `
            #-State $state `
            #-StreetAddress $streetaddress `
            #-OfficePhone $telephone `
            #-EmailAddress $email `
            #-Title $jobtitle `
            #-Department $department
        # If user is created, show message.
        Write-Host "The user account $username is created." -ForegroundColor Cyan
    }
}

Read-Host -Prompt "Press Enter to exit" 
