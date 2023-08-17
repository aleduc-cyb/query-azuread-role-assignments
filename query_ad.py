import requests
import configparser
import sys

# Initialize the configuration parser
config = configparser.ConfigParser()
config.read('config.ini')

# Query AzureAD token based on credentials provided token
def get_auth_headers():
    try:
        # Get config data
        client_id = config.get('AZURE', 'client_id')
        client_secret = config.get('AZURE', 'client_secret')
        tenant_id = config.get('AZURE', 'tenant_id')

        # Configure query params
        token_url = f'https://login.microsoftonline.com/{tenant_id}/oauth2/token'
        token_data = {
            'grant_type': 'client_credentials',
            'client_id': client_id,
            'client_secret': client_secret,
            'resource': 'https://graph.microsoft.com'
        }

        # Query and extract token
        token_response = requests.post(token_url, data=token_data)
        access_token = token_response.json()['access_token']
        return {'Authorization': f'Bearer {access_token}'}
    except Exception as e:
        print('Error while fetching token')
        print(str(e))
        return None

headers = get_auth_headers()

# Get the role id and template id
def get_role_ids(role_name):
    role_url = f'https://graph.microsoft.com/v1.0/directoryRoles?$filter=displayName eq \'{role_name}\''
    roles_response = requests.get(role_url, headers=headers)
    roles = roles_response.json().get('value', [])

    if len(roles) > 0:
        role_id = roles[0]['id']
        role_definition_id = roles[0]['roleTemplateId']
    else:
        print('Role not found')
        sys.exit()

    return role_id, role_definition_id

# Get users with role assigned directly and/or via a group
def get_direct_users(role_id):
    # Get users and groups assigned directly to the role
    direct_assignment_url = f'https://graph.microsoft.com/v1.0/directoryRoles/{role_id}/members'
    direct_assignment_response = requests.get(direct_assignment_url, headers=headers)
    direct_assigned_users_and_groups = direct_assignment_response.json().get('value', [])

    # Extract the users UPNs
    direct_members = []
    for entity in direct_assigned_users_and_groups:
        if 'user' in entity['@odata.type']:
            direct_members.append(entity['userPrincipalName'])
        elif 'group' in entity['@odata.type']:
            group_direct_members = get_group_members(entity['id'])
            if group_direct_members:
                direct_members.extend(group_direct_members)
    
    return direct_members

# Query the members of a group
def get_group_members(group_id):
    members_endpoint = f'https://graph.microsoft.com/v1.0/groups/{group_id}/members'
    members_response = requests.get(members_endpoint, headers=headers)

    users_list = []
    if members_response.ok:
        members = members_response.json().get('value', [])
        for member in members:
            users_list.append(member['userPrincipalName'])
        return users_list
    else:
        return None

# Get users configured in PIM
def get_eligible_users(role_definition_id):
    eligible_assignment_url = f'https://graph.microsoft.com/v1.0/roleManagement/directory/roleEligibilitySchedules?$filter=roleDefinitionId eq \'{role_definition_id}\''
    eligible_assignment_response = requests.get(eligible_assignment_url, headers=headers)
    eligible_assigned_users_and_groups = eligible_assignment_response.json().get('value', [])

    # Extract the users UPNs
    eligible_members = []
    
    for entity in eligible_assigned_users_and_groups:
        id = entity['principalId']
        members_temp = get_group_members(id)
        # If no member have been extracted, the id is probably a user
        if not members_temp:
            users_endpoint = f'https://graph.microsoft.com/v1.0/users/{id}'
            users_response = requests.get(users_endpoint, headers=headers)
            user = users_response.json()
            eligible_members.append(user['userPrincipalName'])
        else:
            eligible_members.extend(members_temp)
    
    return eligible_members

def main():
    role_name = config.get('AZURE', 'role_name')
    role_id, role_definition_id = get_role_ids(role_name)
    direct_users = get_direct_users(role_id)
    eligible_users = get_eligible_users(role_definition_id)
    direct_users.extend(eligible_users)
    return direct_users

if __name__ == "__main__":
    main()