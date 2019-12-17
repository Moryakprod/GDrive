# Vdrive #

1. [General Information](#general-information)
2. [Dependencies](#dependencies)
3. [Installation](#installation)
4. [Development](#development)
5. [Links to servers](#links)


## General Information ##

[vdrive]() is a REST API for [vdrive].
Vdrive for import from google to youtube

## Dependencies ##

Take a look at *requirements.txt* for Python dependencies.

## Installation ##

run once:

```sh
$ make docker_dev
```

## Development ##

If you use Docker Django app will be exposing on 8000 port by default. It's up to you to change settings.

run docker compose:
```sh
$ make docker_dev
```

get docker containers status:
```sh
$ make docker_dev_status
```


run tests in *web* container:
```sh
$ make test
```

Test coverage: 0%

## API ##

For the API description go to:
`api/v1/docs/`

Try API:
`api/v1/swagger/`

Generate OpenAPI schema:
`api/v1/swagger|.json|.yml/`

## Links ##

### Testing server ###

url: *test@example.com*


Generated with [AC's cookiecutter template](https://gl.atomcream.com/boilerplates/templates/django-api-template) version 0.0.1
