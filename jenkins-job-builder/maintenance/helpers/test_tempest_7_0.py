#    Copyright 2016 Mirantis, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from proboscis import test

from fuelweb_test.helpers.decorators import log_snapshot_after_test
from fuelweb_test import settings
from fuelweb_test.tests.base_test_case import SetupEnvironment
from fuelweb_test.tests.base_test_case import TestBasic

@test(groups=["tempest", "tempest.7_0"])
class TempestTest70(TestBasic):
    """TempestCeph."""

    def helper_ceph_services(self, seg_type):
        self.env.revert_snapshot("ready_with_5_slaves")

        cluster_id = self.fuel_web.create_cluster(
            name=self.__class__.__name__,
            mode=settings.DEPLOYMENT_MODE_HA,
            settings={
                "net_provider": 'neutron',
                "net_segment_type": seg_type,
                'volumes_ceph': True,
                'images_ceph': True,
                'ephemeral_ceph': True,
                'objects_ceph': False,
                'volumes_lvm': False,
                'sahara': True,
                'murano': True,
                'ceilometer': True
            }
        )
        self.fuel_web.update_nodes(
            cluster_id,
            {
                'slave-01': ['controller', 'mongo'],
                'slave-02': ['controller', 'mongo'],
                'slave-03': ['controller', 'mongo'],
                'slave-04': ['compute', 'ceph-osd'],
                'slave-05': ['compute', 'ceph-osd']
            }
        )
        # Cluster deploy
        self.fuel_web.deploy_cluster_wait(cluster_id, timeout=60 * 60 * 3)

        # Check network
        self.fuel_web.verify_network(cluster_id)

        self.env.make_snapshot("tempest_test_ceph_{}".format(seg_type),
                               is_make=True)

    def helper_cinder_glance_swift(self, seg_type):
        self.env.revert_snapshot("ready_with_5_slaves")

        cluster_id = self.fuel_web.create_cluster(
            name=self.__class__.__name__,
            mode=settings.DEPLOYMENT_MODE_HA,
            settings={
                "net_provider": 'neutron',
                "net_segment_type": seg_type,
                'volumes_ceph': False,
                'images_ceph': False,
                'objects_ceph': False,
                'volumes_lvm': True,
                'sahara': True,
                'murano': False,
                'ceilometer': False,
            }
        )
        self.fuel_web.update_nodes(
            cluster_id,
            {
                'slave-01': ['controller'],
                'slave-02': ['controller'],
                'slave-03': ['controller'],
                'slave-04': ['compute', 'cinder'],
                'slave-05': ['compute', 'cinder']
            }
        )
        # Cluster deploy
        self.fuel_web.deploy_cluster_wait(cluster_id, timeout=60 * 60 * 3)

        # Check network
        self.fuel_web.verify_network(cluster_id)

        self.env.make_snapshot(
            "tempest_cinder_glance_swift_{}".format(seg_type),
            is_make=True)


    @test(depends_on=[SetupEnvironment.prepare_slaves_5],
          groups=["tempest_ceph_services_tun"])
    @log_snapshot_after_test
    def tempest_ceph_services(self):
        """Deploy env with 3 controller+mongo and 2
           compute +ceph nodes.

        Scenario:
            1. Create cluster
            2. Add 3 nodes with controller role
            3. Add 2 nodes with compute role
            4. Add 2 nodes with cinder and ceph OSD roles
            5. Deploy the cluster
            6. Run OSTF

        Duration 40m
        Snapshot tempest_test_ceph
        """
        self.helper_ceph_services('tun')

    @test(depends_on=[SetupEnvironment.prepare_slaves_5],
          groups=["tempest_cinder_glance_swift_tun"])
    @log_snapshot_after_test
    def tempest_cinder_glance_swift_tun(self):
        """Deploy env with 3 controller and 2 compute nodes.

        Scenario:
            1. Create cluster
            2. Add 3 nodes with controller role
            3. Add 2 nodes with compute role
            4. Deploy the cluster
            5. Run OSTF

        Duration 40m
        Snapshot tempest_cinder_glance_swift_tun
        """
        self.helper_cinder_glance_swift('tun')

    @test(depends_on=[SetupEnvironment.prepare_slaves_5],
          groups=["tempest_cinder_glance_swift_vlan"])
    @log_snapshot_after_test
    def tempest_cinder_glance_swift_vlan(self):
        """Deploy env with 3 controller and 2 compute nodes.

        Scenario:
            1. Create cluster
            2. Add 3 nodes with controller role
            3. Add 2 nodes with compute role
            4. Deploy the cluster
            5. Run OSTF

        Duration 40m
        Snapshot tempest_cinder_glance_swift_tun
        """
        self.helper_cinder_glance_swift('vlan')