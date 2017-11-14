#!/usr/bin/env python
# -*- coding: utf-8 -*-
import click
import configparser
from invoke import run


def get_path_to_confifile():
    return "/home/torsten/Entwicklung/ringo-apps/ringocore/lib/ringo_cli/deploy.cfg"


def get_path_to_dockerfile(config):
    return "/home/torsten/Entwicklung/docker/ringo2-dev"


def get_path_to_ansible(config):
    return "/home/torsten/Entwicklung/ringo-apps/ringocore/ansible"


def build_docker(path, service, version="latest"):
    commands = []
    commands.append("cd {}".format(path))
    commands.append("cat ~/.ssh/id_rsa.pub >> sshkeys")
    commands.append("chmod 644 sshkeys")
    commands.append("docker build -t {}:{} .".format(service, version))
    commands.append("rm sshkeys")
    run(";".join(commands))


def run_docker(service, version="latest"):
    commands = []
    commands.append("docker run \
                    -d \
                    --rm \
                    --name {} \
                    --publish=2222:22 \
                    --publish=5000:5000 \
                    {}:{}".format(service, service, version))
    run(";".join(commands))


def stop_docker(service):
    commands = []
    commands.append("docker stop {}".format(service))
    try:
        run(";".join(commands))
    except Exception as e:
        click.echo(e)


def run_playbook(path_to_ansible, playbook):
    commands = []
    commands.append("cd {}".format(path_to_ansible))
    commands.append("ansible-playbook {} -i hosts".format(playbook))
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

    #deployment = configparser.ConfigParser()
    #deployment.read_file(config)
    # Build new docker docker container
    stop_docker(service)
    path_to_dockerfile = get_path_to_dockerfile(config)
    build_docker(path_to_dockerfile, service)
    run_docker(service)

    # Deploy service in the new docker container
    path_to_ansible = get_path_to_ansible(config)
    run_playbook(path_to_ansible, "playbook.yml")

    # Run the service
    run_service(service, destination)
