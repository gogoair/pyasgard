"""Asgard API mapping."""
INSTANCE_TYPE = 't2.micro'

MAPPING_TABLE = {
    'ami': {
        'show': {
            'path': '/image/show/${ami_id}.json',
            'method': 'GET',
            'status': 200,
        },
        'list': {
            'path': '/image/list.json',
            'method': 'GET',
            'status': 200,
        },
        'push': {
            'path': '/push/startRolling',
            'method': 'POST',
            'status': 200,
            'default_params': {
                'name': '',
                'appName': '',
                'imageId': '',
                'instanceType': INSTANCE_TYPE,
                'keyName': 'jenkins_access',
                'selectedSecurityGroups': ['default'],
                'relaunchCount': 1,
                'kernelId': '',
                'ramdiskId': '',
                'concurrentRelaunches': 1,
                'newestFirst': 'false',
                'checkHealth': 'on',
                'afterBootWait': 30,
            },
        },
    },
    'application': {
        'list': {
            'path': '/application/list.json',
            'method': 'GET',
            'status': 200,
            'instances': {
                'doc': 'List Application Instances.',
                'path': '/instance/list/${app_id}.json',
                'method': 'GET',
                'status': 200,
            },
        },
        'show': {
            'path': '/application/show/${app_name}.json',
            'method': 'GET',
            'status': 200,
        },
        'create': {
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
                'monitorBucketType': 'none',
            },
        },
        'delete': {
            'path': '/application/save',
            'method': 'POST',
            'status': 200,
            'default_params': {
                'name': 'unnecessary',
                '_action_delete': '',
            },
        },
    },
    'asg': {
        'list': {
            'path': '/autoScaling/list.json',
            'method': 'GET',
            'status': 200,
        },
        'show': {
            'path': '/autoScaling/show/${asg_id}.json',
            'method': 'GET',
            'status': 200,
        },
        'delete': {
            'path': '/autoScaling/save',
            'method': 'POST',
            'status': 200,
            'default_params': {
                'name': '',
                '_action_delete': '',
            },
        },
        'create': {
            'path': '/autoScaling/save',
            'method': 'POST',
            'status': 200,
            'valid_params': 'vpc_id',
            'default_params': {
                'appName': '',
                'stack': '',
                'newStack': '',
                'detail': '',
                'countries': '',
                'devPhase': '',
                'hardware': '',
                'partners': '',
                'revision': 0,
                'min': 1,
                'max': 1,
                'desiredCapacity': 0,
                'defaultCooldown': 10,
                'healthCheckType': 'EC2',  # XOR ELB
                'healthCheckGracePeriod': 600,
                'terminationPolicy': 'Default',
                'subnetPurpose': 'app',
                'selectedZones': ['us-east-1b'],
                'azRebalance': 'enabled',
                'selectedLoadBalancersForVpcId${vpc_id}': [''],
                'imageId': '',
                'instanceType': INSTANCE_TYPE,
                'keyName': 'jenkins_access',
                #'pricing': 'SPOT',
                'kernelId': '',
                'ramdiskId': '',
                'iamInstanceProfile': '',
                'selectedSecurityGroups': ['default'],
            },
        },
    },
    'cluster': {
        'list': {
            'path': '/cluster/list.json',
            'method': 'GET',
            'status': 200,
        },
        'enable': {
            'path': '/cluster/save',
            'method': 'POST',
            'status': 200,
            'default_params': {
                'ticket': '',
                'name': '',
                'minAndMaxSize': 1,
                '_action_activate': '',
            },
        },
        'disable': {
            'path': '/cluster/save',
            'method': 'POST',
            'status': 200,
            'default_params': {
                'ticket': '',
                'name': '',
                'minAndMaxSize': 1,
                '_action_deactivate': '',
            },
        },
        # 'create': {
        #     'method': 'POST',
        #     'status': 200,
        # },
        'shrink': {
            'path': '/cluster/save',
            'method': 'POST',
            'status': 200,
            'default_params': {
                'name': '',
                'ticket': '',
                'minAndMaxSize': 1,
                '_action_delete': '',
            },
        },
        'grow': {
            'path': '/cluster/save',
            'method': 'POST',
            'status': 200,
            'default_params': {
                'ticket': '',
                'name': '',
                'noOptionalDefaults': 'true',
                'min': 1,
                'max': 1,
                'desiredCapacity': 0,
                'defaultCooldown': 10,
                'healthCheckType': 'EC2',  # XOR ELB
                'healthCheckGracePeriod': 600,
                'terminationPolicy': 'Default',
                'subnetPurpose': 'app',
                'selectedZones': ['us-east-1b'],
                'azRebalance': 'enabled',
                # We need to figure out a way to do this, or just pass the key
                # 'selectedLoadBalancersForVpcId${vpc_id}': [''],
                'imageId': '',
                'instanceType': INSTANCE_TYPE,
                'keyName': 'jenkins_access',
                'selectedSecurityGroups': ['default'],
                'pricing': 'ON_DEMAND',  # ON_DEMAND=reliable, SPOT=cheaper
                'kernelId': '',
                'ramdiskId': '',
                'iamInstanceProfile': '',
                'afterBootWait': 30,
                'trafficAllowed': 'on',
                '_action_createNextGroup': '',
            },
        },
        'resize': {
            'path': '/cluster/resize',
            'method': 'POST',
            'status': 200,
        },
        'show': {
            'path': '/cluster/show/${cluster_id}.json',
            'method': 'GET',
            'status': 200,
        },
    },
    'deployment': {
        'list': {
            'path': '/deployment/list.json',
            'method': 'GET',
            'status': 200,
        },
        'prepare': {
            'path': '/deployment/prepare/${cluster_id}.json',
            'method': 'GET',
            'status': 200,
        },
        'show': {
            'path': '/deployment/show/${deployment_id}.json',
            'method': 'GET',
            'status': 200,
        },
        'detail': {
            'path': '/ng#/deployment/detail/${deployment_id}.json',
            'method': 'GET',
            'status': 200,
        },
        'start': {
            'path': '/deployment/start',
            'method': 'POST',
            'status': 200,
            'valid_params': ['json'],
        },
    },
    'elb': {
        'list': {
            'path': '/loadBalancer/list.json',
            'method': 'GET',
            'status': 200,
        },
        'delete': {
            'path': '/loadBalancer/save',
            'method': 'POST',
            'status': 200,
            'default_params': {
                'ticket': '',
                'name': '',
                '_action_delete': '',
            },
        },
        'create': {
            'path': '/loadBalancer/save',
            'method': 'POST',
            'status': 200,
            'default_params': {
                'ticket': '',
                'appName': '',
                'stack': '',
                'newStack': '',
                'detail': '',
                'subnetPurpose': 'elb',
                'selectedZones': ['us-east-1b'],
                'selectedSecurityGroups': ['default'],
                'protocol1': 'HTTP',  # XOR TCP
                'lbPort1': 80,
                'instancePort1': 7001,
                'protocol2': '',
                'lbPort2': '',
                'instancePort2': '',
                'target': 'HTTP:7001/healthcheck',
                'interval': 10,
                'timeout': 5,
                'unhealthy': 2,
                'healthy': 10,
                '_action_save': '',
            },
        },
    },
    'instance': {
        # 'create': {
        #     'method': 'POST',
        #     'status': 200,
        # },
        'list': {
            'path': '/instance/list.json',
            'method': 'GET',
            'status': 200,
        },
        'show': {
            'path': '/instance/show/${instance_id}.json',
            'method': 'GET',
            'status': 200,
        },
    },
    'launchconfig': {
        'list': {
            'path': '/launchConfiguration/list.json',
            'method': 'GET',
            'status': 200,
        },
        'show': {
            'path': '/launchConfiguration/show/${config_name}.json',
            'method': 'GET',
            'status': 200,
        },
        'delete': {
            'path': '/launchConfiguration/index',
            'method': 'POST',
            'status': 200,
            'default_params': {
                'name': 'replaceme',
                '_action_delete': '',
            },
        },
        'mass_delete': {
            'path': '/launchConfiguration/index',
            'method': 'POST',
            'status': 200,
            'default_params': {
                'daysAgo': 10,
                '_action_massDelete': '',
            },
        },
    },
    'regions': {
        'list': {
            'path': '/region/list.json',
            'method': 'GET',
            'status': 200,
        },
    },
    'security': {
        'create': {
            'path': '/security/create',
            'method': 'POST',
            'status': 200,
            'default_params': {
                'appName': '',
                'detail': '',
                'enableVpc': 'on',
                'vpcId': '',
                '_enableVpc': '',
                'description': '',
                '_action_save': '',
            },
        },
        'list': {
            'path': '/security/list.json',
            'method': 'GET',
            'status': 200,
        },
        'show': {
            'path': '/security/show.json',
            'method': 'GET',
            'status': 200,
            'default_params': {
                'id': '',
            },
        },
        'delete': {
            'path': '/security/index',
            'method': 'POST',
            'status': 200,
            'default_params': {
                'id': '',
                '_action_delete': '',
            },
        },
    },
    'server': {
        'uptime': {
            'path': '/server/uptime',
            'method': 'GET',
            'status': 200,
        },
        'ip': {
            'path': '/server/ip',
            'method': 'GET',
            'status': 200,
        },
        'build': {
            'path': '/server/build',
            'method': 'GET',
            'status': 200,
        },
    },
    'subnets': {
        'list': {
            'path': '/subnet/list.json',
            'method': 'GET',
            'status': 200,
        },
    },
    'test': {
        'test': {
            'doc': 'Test docstring.',
            'path': '',
            'method': 'GET',
            'status': 200,
        },
    },
}
