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
