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

### DB SETTINGS
SQLALCHEMY_DATABASE_URI = "mysql+pymysql://slam:slam@localhost:3306/slam"
SQLALCHEMY_TRACK_MODIFICATIONS = "False"

#### AUTH SETTINGS
IAM_BASE_URL="https://iam.example.org/"
IAM_CLIENT_ID="MY_CLIENT_ID"
IAM_CLIENT_SECRET="MY_CLIENT_SECRET"
TRUSTED_OIDC_IDP_LIST = [ { 'iss': 'https://iam.example.org/', 'type': 'indigoiam' } ]

#### APP SETTINGS
LOG_LEVEL = "DEBUG"
CMDB_URL = "https://cmdb.example.org"
