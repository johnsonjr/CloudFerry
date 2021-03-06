# Copyright (c) 2015 Mirantis Inc.
#
# Licensed under the Apache License, Version 2.0 (the License);
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an AS IS BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and#
# limitations under the License.

import json

from cloudferry import data_storage
from cloudferry.lib.base.action import action
from cloudferry.lib.utils import log
from cloudferry.condensation import action as c_action
from cloudferry.condensation import process

LOG = log.getLogger(__name__)


class Evacuate(action.Action):

    def __init__(self, iteration, **kwargs):
        self.iteration = iteration
        super(Evacuate, self).__init__(**kwargs)

    def run(self, **kwargs):
        compute_resource = self.cloud.resources['compute']
        cloud = process.SOURCE
        LOG.debug("getting info on cloud %s iteration %s from db", cloud,
                  self.iteration)
        info = data_storage.get(
            c_action.get_key(self.iteration, cloud))
        if not info:
            LOG.info("cannot find info in db on %s-%s", cloud, self.iteration)
            return {}

        actions = json.loads(info).get(c_action.CONDENSE)
        LOG.debug("live-migrating vm one by one")
        for vm_id, dest_host in actions:
            compute_resource.live_migrate_vm(vm_id, dest_host)
        return {}
