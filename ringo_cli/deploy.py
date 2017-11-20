#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import click
import configparser
from invoke import run


def get_services(config):
    services = []
    for section in config.sections():
        if section.startswith("service:"):
            services.append(section.split(":")[1])
    return services


def get_path_to_confifile():
    return "/home/torsten/Entwicklung/ringo-apps/ringocore/lib/ringo_cli/deploy.cfg"


def get_path_to_dockerfile(config):
    return config["build"]["docker"]


def get_ssh_keys(config):
    return config["build"]["ssh"].split("\n")


def get_path_to_ansible(config):
    return config["build"]["ansible"]


def build_docker(path, service, sshkeys, tag="latest"):
    commands = []
    commands.append("cd {}".format(path))
    for key in sshkeys:
        commands.append("cat {} > sshkeys".format(key))
    commands.append("chmod 644 sshkeys")
    commands.append("docker build -t {}:{} .".format(service, tag))
    commands.append("rm sshkeys")
    run(";".join(commands))


def run_docker(service, tag="latest"):
    commands = []
    commands.append("docker run \
                    -d \
                    --rm \
                    --name {} \
                    --publish=2222:22 \
                    --publish=5000:5000 \
                    {}:{}".format(service, service, tag))
    run(";".join(commands))


def stop_docker(service):
    commands = []
    commands.append("docker stop {}".format(service))
    try:
        run(";".join(commands))
    except Exception as e:
        click.echo(e)


def run_playbook(path_to_ansible, playbook, config):
    extra_vars = " ".join([
        "voorhees_version={}".format(config["voorhees_version"]),
        "service_version={}".format(config["service_version"]),
        "storage_version={}".format(config["storage_version"]),
        "core_version={}".format(config["core_version"]),
        "version={}".format(config["version"])
    ])
    commands = []
    commands.append("cd {}".format(path_to_ansible))
    commands.append("ansible-playbook {} \
                    -i hosts \
                    --extra-vars '{}' \
                    ".format(playbook, extra_vars))
    run(";".join(commands))


def run_service(service, host):
    commands = []
    commands.append("ssh root@{} \
                     -o StrictHostKeyChecking=no \
                     -p 2222 '{}'".format(host, service))
    run(";".join(commands))


@click.command()
@click.option("--config",
              help="Configuration file for deployment",
              default=get_path_to_confifile(),
              type=click.File('r'))
@click.option("--version",
              help="Version to build. E.g 1.0",
              default="master")
@click.option("--destination",
              help="Where should the service be deployed",
              default="localhost",
              type=click.Choice(['localhost']))
@click.argument("service")
@click.pass_context
def deploy(ctx, config, service, version, destination):
    """Deploy a service"""

    deployment = configparser.ConfigParser()
    deployment.read_file(config)

    # Check if given service is valid
    services = get_services(deployment)
    if service not in services:
        click.secho("Invalid service!", fg="red")
        click.echo("Can not find service in {}.\n"
                   "Please choose from [{}]".format(config.name, ", ".join(services)))
        sys.exit(1)

    # Build new docker docker container
    stop_docker(service)
    path_to_dockerfile = get_path_to_dockerfile(deployment)

    sshkeys = get_ssh_keys(deployment)
    build_docker(path_to_dockerfile, service, sshkeys)
    run_docker(service)

    # Deploy service in the new docker container
    service_config = deployment["service:{}".format(service)]
    path_to_ansible = get_path_to_ansible(deployment)
    run_playbook(path_to_ansible, "playbook.yml", service_config)

    # Run the service
    #run_service(service, destination)
