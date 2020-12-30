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
import re

class IndigoTokenDecoder:
    def get_groups(self, info):
        return info['groups']

class EgiTokenDecoder:
    def get_groups(self, info):
        memberships = info['eduperson_entitlement']
        pattern = 'urn:mace:egi.eu:group:(.*):role=vm_operator#aai.egi.eu'

        groups=[]
        for m in memberships:
            match = re.search(pattern, m)
            if match:
                groups.append(match.group(1))

        return groups

class TokenDecoderFactory:

    def __init__(self):
        self._creators = {}

    def register_format(self, format, creator):
        self._creators[format] = creator

    def get_decoder(self, format):
        creator = self._creators.get(format)
        if not creator:
            raise ValueError(format)
        return creator()


factory = TokenDecoderFactory()
factory.register_format('indigoiam', IndigoTokenDecoder)
factory.register_format('egicheckin', EgiTokenDecoder)


