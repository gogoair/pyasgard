"""Asgard API mapping."""
INSTANCE_TYPE = 't2.micro'

MAPPING_TABLE = {
    'ami': {
        'show': {
            'doc': """Show details for an AMI.

            Args:
                ami_id: ID of an existing AMI.
            """,
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
                'doc': """List Application Instances.

                Args:
                    app_id: Name of an existing Application.
                """,
                'path': '/instance/list/${app_id}.json',
                'method': 'GET',
                'status': 200,
            },
        },
        'show': {
            'doc': """Show details for an Application.

            Args:
                app_name: Name of an existing Application.
            """,
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
            'doc': """Show details for an ASG.

            Args:
                asg_id: ID of an existing ASG.
            """,
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
            'doc': """Create an ASG.

            Before calling this command, the MAPPING_TABLE must be modified to
            insert a dynamically constructed key::

                client = Asgard('http://test.com')
                vpc_id = 'vpc-something'
                lb_list = ['lb-something']
                lb_param = 'selectedLoadBalancersForVpcId{0}'.format(vpc_id)

                api = client.mapping_table['asg']['create']['default_params']
                api[lb_param] = lb_list

                client.asg.create(**{lotsofparams})

            This will translate into the correct parameter passed to Asgard.
            """,
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
                # 'selectedLoadBalancersForVpcId${vpc_id}': [''],
                'imageId': '',
                'instanceType': INSTANCE_TYPE,
                'keyName': 'jenkins_access',
                # 'pricing': 'SPOT',
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
            'doc': """Show details for a Cluster.

            Args:
                cluster_id: ID of an existing Cluster.
            """,
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
            'doc': """Generate JSON for customizing an Asgard Deployment.

            Args:
                cluster_id: ID of an existing Cluster.
            """,
            'path': '/deployment/prepare/${cluster_id}.json',
            'method': 'GET',
            'status': 200,
        },
        'show': {
            'doc': """Show details for an Asgard Deployment.

            Args:
                deployment_id: ID of a running Deployment.
            """,
            'path': '/deployment/show/${deployment_id}.json',
            'method': 'GET',
            'status': 200,
        },
        'detail': {
            'doc': """Show details for an Asgard Deployment.

            Args:
                deployment_id: ID of a running Deployment.
            """,
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
        'show': {
            'doc': """Show details for an ELB.

            Args:
                elb_id: ID of an existing ELB.
            """,
            'path': '/loadBalancer/show/${elb_id}.json',
            'method': 'GET',
            'status': 200,
        },
        'update': {
            'doc': """Update ELB configuration with new settings.""",
            'path': '/loadBalancer/index',
            'method': 'POST',
            'status': 200,
            'default_params': {
                'ticket': '',
                'name': '',
                'selectedZones': ['us-east-1b'],
                'target': 'TCP:8080',
                'interval': 10,
                'timeout': 5,
                'unhealthy': 2,
                'healthy': 2,
                '_action_update': '',
            },
        },
        'listener': {
            'doc': """Manipulate listeners for an existing ELB.""",
            '_branch': '',
            'add': {
                'doc': """Add a listener to an existing ELB.

                Args:
                    name: Name of the Load Balancer.
                    protocol: Can be either HTTP or TCP.
                    lbPort: Int of the port which the ELB will listen on,
                        cannot be in use by another listener.
                    instancePort: Int of the port which Instances are using.
                """,
                'path': '/loadBalancer/save',
                'method': 'POST',
                'status': 200,
                'default_params': {
                    'ticket': '',
                    'protocol': 'HTTP',
                    'lbPort': 80,
                    'instancePort': 8080,
                    'name': '',
                    '_action_addListener': '',
                },
            },
            'remove': {
                'doc': """Remove a listener from an existing ELB.

                Args:
                    name: Name of the Load Balancer.
                    lbPort: Int for the Load Balancer port number.
                """,
                'path': '/loadBalancer/save',
                'method': 'POST',
                'status': 200,
                'default_params': {
                    'ticket': '',
                    'name': '',
                    'lbPort': 80,
                    '_action_removeListener': '',
                }
            },
        }
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
            'doc': """Show details for an Instance.

            Args:
                instance_id: ID of an existing Instance.
            """,
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
            'doc': """Show details for a Launch Configuration.

            Args:
                config_name: Name of an existing Launch Configuration.
            """,
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
    'rds': {
        'list': {
            'path': '/rdsInstance/list.json',
            'method': 'GET',
            'status': 200,
        },
        'show': {
            'path': '/rdsInstance/show/${name}.json',
            'method': 'GET',
            'status': 200,
        },
    },
    'rdssecurity': {
        'list': {
            'path': '/dbSecurity/list.json',
            'method': 'GET',
            'status': 200,
        },
        'show': {
            'path': '/dbSecurity/show/${name}.json',
            'method': 'GET',
            'status': 200,
        },
    },
    'rdssnapshot': {
        'list': {
            'path': '/dbSnapshot/list.json',
            'method': 'GET',
            'status': 200,
        },
        'show': {
            'path': '/dbSnapshot/show/${name}.json',
            'method': 'GET',
            'status': 200,
        },
    },
    'regions': {
        'list': {
            'path': '/region/list.json',
            'method': 'GET',
            'status': 200,
        },
    },
    'sdb': {
        'list': {
            'path': '/domain/list.json',
            'method': 'GET',
            'status': 200,
        },
        'show': {
            'path': '/domain/show/${name}.json',
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
    'sns': {
        'list': {
            'path': '/topic/list.json',
            'method': 'GET',
            'status': 200,
        },
        'show': {
            'path': '/topic/show/${name}.json',
            'method': 'GET',
            'status': 200,
        },
    },
    'sqs': {
        'list': {
            'path': '/queue/list.json',
            'method': 'GET',
            'status': 200,
        },
        'show': {
            'path': '/queue/show/${name}.json',
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
    'task': {
        'list': {
            'path': '/task/list.json',
            'method': 'GET',
            'status': 200,
        },
        'show': {
            'path': '/task/show/${id}.json',
            'method': 'GET',
            'status': 200,
        },
    },
    'test': {
        'doc': 'Test commands.',
        'test': {
            'doc': 'Test docstring.',
            'path': '',
            'method': 'GET',
            'status': 200,
        },
    },
}
