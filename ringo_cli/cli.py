# -*- coding: utf-8 -*-

import click
import requests
import voorhees

SERVICES = {
        "users": {"url": "http://0.0.0.0:5000"}
}


@click.group()
@click.pass_context
def main(ctx):
    """CLI for the Ringo2 core service."""
    ctx.obj = {}
    pass


@click.group()
@click.argument('service', type=click.Choice(SERVICES))
@click.pass_context
def crud(ctx, service):
    """Send basic CRUD commands to a service."""
    ctx.obj["service"] = service


@click.group()
@click.pass_context
def admin(ctx):
    """Various administration commands."""
    pass


@click.command()
@click.argument('jsonfile', type=click.File('rb'))
@click.pass_context
def create(ctx, jsonfile):
    """Creates a new item on the service.
    The new item is initialised with the values defined in the JSON
    file. Create is called for every dataset within the JSON file.
    """
    data = voorhees.from_json(jsonfile.read())
    if not isinstance(data, list):
        data = [data]

    total = len(data)
    service = ctx.obj["service"]
    for num, item in enumerate(data):
        click.echo('Creating ({}/{}) -> '.format(num+1, total), nl=False)
        response = requests.post("{}/{}".format(SERVICES[service]["url"], service), data=voorhees.to_json(item))
        color = "red" if (response.status_code >= 300) else "green"
        click.echo(click.style('{}'.format(response.status_code), fg=color))


@click.command()
@click.argument('id', type=click.INT)
@click.pass_context
def read(ctx, id):
    service = ctx.obj["service"]
    response = requests.get("{}/{}/{}".format(SERVICES[service]["url"], service, id))
    if (response.status_code >= 300):
        color = "red"
        click.echo('Reading ID:{} -> '.format(id), nl=False)
        click.echo(click.style('{}'.format(response.status_code), fg=color))
    else:
        print(voorhees.prettify(response.text))


@click.command()
@click.argument('jsonfile', type=click.File('rb'))
@click.pass_context
def update(ctx, jsonfile):
    data = voorhees.from_json(jsonfile.read())
    if not isinstance(data, list):
        data = [data]

    total = len(data)
    service = ctx.obj["service"]
    for num, item in enumerate(data):
        click.echo('Updating ID:{} ({}/{}) -> '.format(item["id"], num+1, total), nl=False)
        response = requests.put("{}/{}/{}".format(SERVICES[service]["url"], service, item["id"]),
                                data=voorhees.to_json(item))
        color = "red" if (response.status_code >= 300) else "green"
        click.echo(click.style('{}'.format(response.status_code), fg=color))


@click.command()
@click.argument('id', type=click.INT)
@click.pass_context
def delete(ctx, id):
    click.echo('Deleting ID:{} -> '.format(id), nl=False)
    service = ctx.obj["service"]
    response = requests.delete("{}/{}/{}".format(SERVICES[service]["url"], service, id))
    color = "red" if (response.status_code >= 300) else "green"
    click.echo(click.style('{}'.format(response.status_code), fg=color))


@click.command()
@click.pass_context
def search(ctx):
    service = ctx.obj["service"]
    response = requests.get("{}/{}".format(SERVICES[service]["url"], service))
    if (response.status_code >= 300):
        color = "red"
        click.echo('Searching -> ', nl=False)
        click.echo(click.style('{}'.format(response.status_code), fg=color))
    else:
        print(voorhees.prettify(response.text))


main.add_command(crud)
main.add_command(admin)

crud.add_command(search)
crud.add_command(create)
crud.add_command(read)
crud.add_command(update)
crud.add_command(delete)


if __name__ == "__main__":
    main()
