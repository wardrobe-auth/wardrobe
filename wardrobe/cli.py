import os

import click



@click.group()
def main():
    pass


@main.add_command
@click.command()
def hello():
    click.echo('hello, world')


if __name__ == '__main__':
    main()

