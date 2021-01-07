# Copyright (c) Istituto Nazionale di Fisica Nucleare (INFN). 2019-2020
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import requests

class Client:
    """
    This is Cmdb client class that lets you access the main Cmdb API

    Parameters
    ------------
        base_url: str
        Sets base URL to make request to.

    """

    def __init__(self, base_url, timeout=30, cacert = None):
        self.timeout = timeout
        self.base_url = base_url
        self.verify = cacert if cacert else True


    def is_valid_service(self, service_id):
        url = "{}/service/id/{}".format(self.base_url, service_id)
        response = requests.get(url, timeout=self.timeout, verify=self.verify)

        if response.ok:
            return True
        else:
            return False

    def get_services(self, detailed=False):
        option = "?include_docs=true" if detailed else ""
        url = "{}/service/list{}".format(self.base_url, option)
        response = requests.get(url, timeout=self.timeout, verify=self.verify)

        if response.ok:
            return response.json()['rows']
        else:
            return None

    def get_service(self, id, detailed=False):
        option = "?include_docs=true" if detailed else ""
        url = "{}/service/id/{}{}".format(self.base_url, id, option)
        response = requests.get(url, timeout=self.timeout, verify=self.verify)

        if response.ok:
            return response.json()['data']
        else:
            return None