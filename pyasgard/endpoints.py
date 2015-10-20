"""Asgard API mapping."""

MAPPING_TABLE = {
    'list_regions': {
        'path': '/region/list.json',
        'method': 'GET',
        'status': 200,
    },
    'list_instances': {
        'path': '/instance/list.json',
        'method': 'GET',
        'status': 200,
    },
    'list_applications': {
        'path': '/application/list.json',
        'method': 'GET',
        'status': 200,
    },
    'show_application': {
        'path': '/application/show/${app_name}.json',
        'method': 'GET',
        'status': 200,
    },
    'create_application': {
        'path': '/application/save',
        'method': 'POST',
        'status': 200,
        'valid_params': ['name', 'group', 'description', 'owner', 'email'],
        'default_params': {
            'name': 'unneccessary',
            'group': 'Replaceable',
            'type': 'Web Service',
            'description': 'Poor description.',
            'owner': 'Bashful',
            'email': 'invalid@gogoair.com',
            'monitorBucketType': 'none'
        },
    },
    'delete_application': {
        'path': '/application/save',
        'method': 'POST',
        'status': 200,
        'default_params': {
            'name': 'unnecessary',
            '_action_delete': '',
        },
    },
    'list_application_instances': {
        'path': '/instance/list/${app_id}.json',
        'method': 'GET',
        'status': 200,
    },
    'show_instance': {
        'path': '/instance/show/${instance_id}.json',
        'method': 'GET',
        'status': 200,
    },
    'show_auto_scaling_group': {
        'path': '/autoScaling/show/${asg_id}.json',
        'method': 'GET',
        'status': 200,
    },
    'list_clusters': {
        'path': '/cluster/list.json',
        'method': 'GET',
        'status': 200,
    },
    'cluster_resize': {
        'path': '/cluster/resize',
        'method': 'POST',
        'status': 200,
    },
    'show_cluster': {
        'path': '/cluster/show/${cluster_id}.json',
        'method': 'GET',
        'status': 200,
    },
    'show_ami': {
        'path': '/image/show/${ami_id}.json',
        'method': 'GET',
        'status': 200,
    },
    'list_launchconfigs': {
        'path': '/launchConfiguration/list.json',
        'method': 'GET',
        'status': 200,
    },
    'show_launchconfig': {
        'path': '/launchConfiguration/show/${config_name}.json',
        'method': 'GET',
        'status': 200,
    },
    'list_elb': {
        'path': '/loadBalancer/list.json',
        'method': 'GET',
        'status': 200,
    },
    'server_uptime': {
        'path': '/server/uptime',
        'method': 'GET',
        'status': 200,
    },
    'server_ip': {
        'path': '/server/ip',
        'method': 'GET',
        'status': 200,
    },
    'server_build': {
        'path': '/server/build',
        'method': 'GET',
        'status': 200,
    },
    'delete_launchconfig': {
        'path': '/launchConfiguration/index',
        'method': 'POST',
        'status': 200,
        'default_params': {'name': 'replaceme',
                           '_action_delete': ''},
    },
    'mass_delete_launchconfigs': {
        'path': '/launchConfiguration/index',
        'method': 'POST',
        'status': 200,
        'default_params': {'daysAgo': 10,
                           '_action_massDelete': ''},
    }
}
