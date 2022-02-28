import json
import requests
from requests.api import get, head

def get_octopus_resource(uri, headers, skip_count = 0):
    items = []
    skip_querystring = ""

    if '?' in uri:
        skip_querystring = '&skip='
    else:
        skip_querystring = '?skip='

    response = requests.get((uri + skip_querystring + str(skip_count)), headers=headers)
    response.raise_for_status()

    # Get results of API call
    results = json.loads(response.content.decode('utf-8'))

    # Store results
    if 'Items' in results.keys():
        items += results['Items']

        # Check to see if there are more results
        if (len(results['Items']) > 0) and (len(results['Items']) == results['ItemsPerPage']):
            skip_count += results['ItemsPerPage']
            items += get_octopus_resource(uri, headers, skip_count)

    else:
        return results

    
    # return results
    return items

# Define Octopus server variables
octopus_server_uri = 'https://octopus.paraport.com/app#'
octopus_api_key = 'API-XV3JNMZKACUKOOM2MOSJ7GWB1U'
headers = {'X-Octopus-ApiKey': octopus_api_key}
space_name = 'Default_1'
tenant_name = 'MyTenant_1'
project_names = ['MyProject_1']
environment_names = ['Development', 'Test']

# Get space
uri = '{0}/api/spaces'.format(octopus_server_uri)
spaces = get_octopus_resource(uri, headers)
space = next((x for x in spaces if x['Name'] == space_name), None)

# Get projects
uri = '{0}/api/{1}/projects'.format(octopus_server_uri, space['Id'])
projects = get_octopus_resource(uri, headers)
tenantProjects = []
for project_name in project_names:
    project = next((x for x in projects if x['Name'] == project_name), None)
    if None != project:
        tenantProjects.append(project['Id'])
    else:
        print ('{0} not found!'.format(project_name))

# Get environments
uri = '{0}/api/{1}/environments'.format(octopus_server_uri, space['Id'])
environments = get_octopus_resource(uri, headers)
tenantEnvironments = []
for environment_name in environment_names:
    environment = next((x for x in environments if x['Name'] == environment_name), None)
    if None != environment:
        tenantEnvironments.append(environment['Id'])

# Create project/environment dictionary
projectEnvironments = {}
for project in tenantProjects:
    projectEnvironments[project] = tenantEnvironments

# get Tenant Id
uri = '{0}/api/{1}/tenants'.format(octopus_server_uri, space['Id'])
tenants = get_octopus_resource(uri, headers)
tenant = next((t for t in tenants if t['Name'] == tenant_name), None)

if tenant:
    print ('Tenant already exists:',tenant_name,'with Tenant-ID:',tenant['Id'])
else:
    # Create new Tenant
    print(tenant_name,'tenant does not exist')
tenant = {
    'Name': tenant_name,
    'SpaceId': space['Id'],
    'ProjectEnvironments': projectEnvironments
}

uri = '{0}/api/{1}/tenants'.format(octopus_server_uri, space['Id'])
response = requests.post(uri, headers=headers, json=tenant)
response.raise_for_status

