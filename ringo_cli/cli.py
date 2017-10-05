# -*- coding: utf-8 -*-

import click
import requests
import voorhees

SERVICES = {
    "users": {}
}


@click.group()
def main():
    pass


@click.command()
@click.argument('service', type=click.Choice(SERVICES))
@click.argument('jsonfile', type=click.File('rb'))
def create(service, jsonfile):
    """Creates a new item on the service.
    The new item is initialised with the values defined in the JSON
    file. Create is called for every dataset within the JSON file.
    """
    data = voorhees.from_json(jsonfile.read())
    if not isinstance(data, list):
        data = [data]

    total = len(data)
    for num, item in enumerate(data):
        click.echo('Importing ({}/{}) -> '.format(num+1, total), nl=False)
        response = requests.post("http://0.0.0.0:5000/users", data=voorhees.to_json(item))
        color = "red" if (response.status_code >= 300) else "green"
        click.echo(click.style('{}'.format(response.status_code), fg=color))


@click.command()
@click.argument('service', type=click.Choice(SERVICES))
@click.argument('id', type=click.INT)
def read(service, id):
    response = requests.get("http://0.0.0.0:5000/users/{}".format(id))
    print(response.json())


@click.command()
@click.argument('service', type=click.Choice(SERVICES))
@click.argument('jsonfile', type=click.File('rb'))
def update(service, jsonfile):
    data = voorhees.from_json(jsonfile.read())
    if not isinstance(data, list):
        data = [data]

    total = len(data)
    for num, item in enumerate(data):
        click.echo('Updating ({}/{}) -> '.format(num+1, total), nl=False)
        response = requests.put("http://0.0.0.0:5000/users/{}".format(item["id"]), data=voorhees.to_json(item))
        color = "red" if (response.status_code >= 300) else "green"
        click.echo(click.style('{}'.format(response.status_code), fg=color))


@click.command()
@click.argument('service', type=click.Choice(SERVICES))
@click.argument('id', type=click.INT)
def delete(service, id):
    click.echo('Deleting {} -> '.format(id), nl=False)
    response = requests.delete("http://0.0.0.0:5000/users/{}".format(id))
    color = "red" if (response.status_code >= 300) else "green"
    click.echo(click.style('{}'.format(response.status_code), fg=color))


main.add_command(create)
main.add_command(read)
main.add_command(update)
main.add_command(delete)


if __name__ == "__main__":
    main()
