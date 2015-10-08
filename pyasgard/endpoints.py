"""
API MAPPING
"""
mapping_table = {
    # Asgard API
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
    'list_application_instances': {
        'path': '/instance/{{app_id}}.json',
        'method': 'GET',
        'status': 200,
    },
    'show_instance': {
        'path': '/instance/show/{{instance_id}}.json',
        'method': 'GET',
        'status': 200,
    },
    'show_auto_scaling_group': {
        'path': '/autoScaling/show/{{scaling_group_id}}.json',
        'method': 'GET',
        'status': 200,
    },
    'resize_cluster': {
        'path': '/cluster/resize',
        'method': 'POST',
        'status': 200,
    },
    'show_cluster': {
        'path': '/cluster/show/{{app_id}}.json',
        'method': 'GET',
        'status': 200,
    },
    'show_ami': {
        'path': '/image/show/{{ami_id}}.json',
        'method': 'GET',
        'status': 200,
    },
    'cluster_resize': {
        'path': '/cluster/resize',
        'valid_params': ('name', 'minAndMaxSize'),
        'method': 'GET',
        'status': 200,
    },
}
