# The SLS Simple Log Server
This is a low tech log server with the main functions:

- collect logs sent to the server via HTTP-requests
- parse the requests according to a configuration
- display the logs in a searchable web-interface
- provide a plugin support to futher process logs

Many log server solutions exist, but none fit my requirements of flexibility and simplicity (as with much of my other *simple-something* projects).

## Parse Config
The directory *parsing/* may contain *JSON* files, indicating a formating, for one or more services, in the form of:

    {
        "service_name" : {
            "strict" : true/false,
            "format" : "REGEX_FORMAT"
        },
    }

If `strict` is true, reject all lines, which do not fit the indicated format. The content of `format` will be fed to the python-`re` module and use to parse any lines of type `SIMPLE`.

## PUT/POST Request
`/submitt` expects a *JSON*-request in the form of:

    {
        "service" : "service_name",
        "host"    : "optional_host",
        "content" : "log_content",
        "type"    : "log_type"
    }

## Log Types
- `SIMPLE` - a single log line
- `MULTILINE` - multi-line content, for example a stacktrace

## Plugins
The `plugins/`-dir may contain python plugin scripts. These scripts must provide the function:

    onSubmit(contentType, service, host, content)

and a variable `APPLY_TO_SERVICE` set to a list of service names for which this plugin should be ranor `None`, to apply it to all services regardless of name.

    # apply to service 1 & 2
    APPLY_TO_SERVICE = [ "serivce_1", "service_2" ]

    # or apply to all services
    APPLY_TO_SERVICE = None

## Nginx for HTTPS/Basic-Auth
You can use `mkpasswd` to create an auth-file via

    echo user >> authfile
    mkpasswd -m sha512crypt >> authfile
    <input password>

For information about HTTP with nginx refer to [this tutorial](https://medium.com/anti-clickbait-coalition/hassle-free-ssl-with-nginx-f34ddcacf197).

    server {

        listen 80;
        listen 443 ssl;
        listen [::]:80;
        listen [::]:443 ssl;

        server_name _;
        access_log /var/log/nginx/sls;

        auth_basic "Log Server SLS Auth";
        auth_basic_user_file "/path/to/auth/file";

        location / {
            proxy_pass http://host:port;
        }
    }

## Submissions
If you are not running a reverse proxy with *Basic-Auth*, you may omit any authentication related code.

**python**

    import requests
    url      = http://host/submit
    jsonDict = { "service"     : "service_name",
                 "host"        : "hostname",
                 "contentType" : "contentType",
                 "severity"    : NUMBER, # 0 -7
                 "content"     : "content" }

    auth = requests.auth.HTTPBasicAuth(app.config["LOG_AUTH_USER"], app.config["LOG_AUTH_PASS"])
    r = requests.put(url, json=jsonDict, auth=auth)
    print(r.status, r.text)

**curl**

    curl -u user:pass -H "Content-Type: application/json" -X PUT http://host/submit -d
        '{ "service"     : "service_name",
          "host"        : "hostname",
          "contentType" : "contentType",
          "severity"    : NUMBER, # 0 -7
          "content"     : "content" }'
