# query-azuread-role-assignments
Code to query all assignments (direct and eligible) for a role

Just fill the config file with your app info and the role for which you want the data

The following application permissions are needed:
- Directory.Read.All
- Group.Read.All	
- GroupMember.Read.All
- PrivilegedAccess.Read.AzureAD	
- RoleManagement.Read.All
- User.Read.All 