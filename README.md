# slat
Service Level Agreement Tool

## How to deploy slat
Register a client in IAM with the following properties:

- redirect uri: `https://<SLAT_HOST>:<PORT>/login/iam/authorized`
- scopes: 'openid', 'email', 'profile', 'offline_access'

Create the folder `instance` to put the application configuration file:
 - (mandatory) `config.json` file (see the example below)
 
````
instance
|____config.json
````

| Parameter name  | Description | Mandatory (Y/N) | Default Value 
| -------------- | ------------- |------------- |------------- |
| IAM_BASE_URL | Base URL of the IAM used for the authenticated access to the slat dashboard  | Y | N/A
| IAM_CLIENT_ID | IAM client ID | Y | N/A
| IAM_CLIENT_SECRET | IAM client Secret | Y | N/A
| TRUSTED_OIDC_IDP_LIST | List of OpenID-Connect IdPs that are trusted by the slat app.<br>The REST API endpoint can be accessed using access tokens issued by IdPs in this list  | Y | N/A.<br>The format of this field is:<br> <code> [ { 'iss': 'https://iam.example.org/', 'type': 'indigoiam' }, { 'iss': 'https://iam2.example.org/', 'type': 'indigoiam' }  ] </code>
| SQLALCHEMY_DATABASE_URI | The database URI that should be used for the connection | N | Default: "mysql+pymysql://slat:slat@localhost:3306/slat"
| LOG_LEVEL | Logging level | N | Default: INFO
| CMDB_URL | URL of the CMDB to retrieve information about the services | Y | N/A

Here is an example of config.json:
````
{
{
  "SQLALCHEMY_DATABASE_URI": "mysql+pymysql://slat:slat@localhost:3310/slat",
  "CMDB_URL": "https://indigo-paas.cloud.infn.it/cmdb",
  "TRUSTED_OIDC_IDP_LIST": [
    {
      "iss": "https://iam-test.indigo-datacloud.eu/",
      "type": "indigoiam"
    }
  ],
  "IAM_BASE_URL": "https://iam-test.indigo-datacloud.eu/",
  "IAM_CLIENT_ID": "THIS-IS-MYCLI-ENTID",
  "IAM_CLIENT_SECRET": "THISISMYCLIENTSECRET"
}

}
````

You need to run slat on HTTPS (otherwise you will get an error); you can choose between
- enabling the HTTPS support
- using an HTTPS proxy

Details are provided in the next paragraphs.

### Enabling HTTPS

You would need to provide
- a pair certificate/key that the container will read from the container paths `/certs/cert.pem` and `/certs/key.pem`;
- the environment variable `ENABLE_HTTPS` set to `True`
 

Run the docker container:
```
docker run -d -p 443:5001 --name='slat' \
           -e ENABLE_HTTPS=True \
           -v $PWD/cert.pem:/certs/cert.pem \
           -v $PWD/key.pem:/certs/key.pem \
           -v $PWD/instance:/app/instance \
           marica/slat:latest
```
Access slat UI at `https://<SLAT_HOST>/`

### Using an HTTPS Proxy 

Example of configuration for nginx:
```
server {
      listen         80;
      server_name    YOUR_SERVER_NAME;
      return         301 https://$server_name$request_uri;
}

server {
  listen        443 ssl;
  server_name   YOUR_SERVER_NAME;
  access_log    /var/log/nginx/proxy.access.log  combined;

  ssl on;
  ssl_protocols TLSv1 TLSv1.1 TLSv1.2;
  ssl_certificate           /etc/nginx/cert.pem;
  ssl_certificate_key       /etc/nginx/key.pem;
  ssl_trusted_certificate   /etc/nginx/trusted_ca_cert.pem;

  location / {
                # Pass the request to Gunicorn
                proxy_pass http://127.0.0.1:5001/;

                proxy_set_header        X-Real-IP $remote_addr;
                proxy_set_header        X-Forwarded-For $proxy_add_x_forwarded_for;
                proxy_set_header        X-Forwarded-Proto https;
                proxy_set_header        Host $http_host;
                proxy_redirect          http:// https://;
                proxy_buffering         off;
  }

}
```

Run the docker container:

```
docker run -d -p 5001:5001 --name='slat' \
           -v $PWD/instance:/app/instance \
           marica/slat:latest
```
:warning: Remember to update the redirect uri in the IAM client to `https://<PROXY_HOST>/login/iam/authorized`

Access slat UI at `https://<PROXY_HOST>/`

### Performance tuning

You can change the number of gunicorn worker processes using the environment variable WORKERS.
E.g. if you want to use 2 workers, launch the container with the option `-e WORKERS=2`
Check the [documentation](http://docs.gunicorn.org/en/stable/design.html#how-many-workers) for ideas on tuning this parameter.

## How to build the docker image

```
git clone https://github.com/maricaantonacci/slat.git
cd slat
docker build -f docker/Dockerfile -t slat .
```

## How to setup a development environment

```
git clone https://github.com/maricaantonacci/slat.git
cd slat
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
```

Run the script for DB setup:
```
python3 manage.py db upgrade
```

Start the slat app:
```
FLASK_app=slat flask run --host=0.0.0.0 --cert cert.pem --key privkey.pem --port 443
```

## DB prerequisites:

```
You must have a running instance of MySql
You must have/create a user with full db administration rights to auto create/manage the database
```
