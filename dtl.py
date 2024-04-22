#!/usr/bin/env python3
"""A cli for creating and opening multiple Darktable libraries."""

import sqlite3
import os
import subprocess
import click
import osutil
import shlex
import shutil

__version__ = '0.2'


conf = {}

def _set_config_paths(project_path):
    conf['configdir'] = project_path + '/.darktable'
    conf['cachedir'] = project_path + '/.darktable/cache'
    conf['librarydb'] = project_path + '/.darktable/library.db'
    conf['last'] = project_path + '/.darktable/.last_location'
    conf['firstfun'] = project_path + '/.darktable/.firstrun'
    conf['rc'] = project_path + '/.darktable/darktablerc'


def _launch_dt(darktable, detach):
    """Launch Darktable"""

    librarydb = conf['librarydb']
    cachedir = conf['cachedir']
    configdir = conf['configdir']
    firstrun = conf['firstfun']

    # Check if this is the first time opening the project.
    if osutil.file_exists(firstrun):
        # Remove the firstrun file.
        osutil.rm(firstrun)

    cmd_options = '--cachedir ' + cachedir + ' --configdir ' + configdir + ' --library ' + librarydb

    cmd = shlex.split(darktable + ' ' + cmd_options)
    click.secho('[Running] ' + darktable + ' ' + cmd_options)

    if detach:
        subprocess.Popen(cmd, start_new_session=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        subprocess.run(cmd, start_new_session=False)


def _format_path(path):
    """Formats the targeted path.
        Expands a relative path to an absolute path while also removing any trailing slash."""

    # If path ends with a `/`. If so remove it.
    if str(path).endswith('/'):
        path = path.rstrip('/')

    # Convert to an absolute path.
    path = os.path.abspath(path)

    return path

def _update_base_path(library, old_path, new_path):
    click.secho('Updating film roll location', fg='yellow')

    conn = sqlite3.connect(library)
    cur = conn.cursor()
    film_rolls = cur.execute("""select id, folder from film_rolls""")

    counter = 0
    for film_roll in film_rolls.fetchall():
        if str(film_roll[1]).startswith(old_path):
            new_folder = str(film_roll[1]).replace(old_path, new_path)
            cur.execute("""update film_rolls set folder='%s' where id='%s'""" % (new_folder, film_roll[0]))
            counter += 1
    conn.commit()
    conn.close()
    osutil.echo(new_path, dst=conf['last'])
    click.echo("Updated %s film roll(s) from %s to %s" % (counter, old_path, new_path))

    # Replace all instances of the old location with the new location in darktablerc
    rc_content = osutil.cat(conf['rc'])
    click.secho('Updating darktablerc', fg='white')
    osutil.echo(rc_content.replace(old_path, new_path), dst=conf['rc'])


@click.group()
@click.version_option(version=__version__, message=__version__)
def cli():
    """A cli for creating and opening multiple Darktable libraries."""
    pass

@cli.command('create')
@click.argument('project_path')
@click.option('--init', is_flag=True, help="Use an existing directory")
def new_project(project_path, init=False):
    """Create a new project"""

    project_path = _format_path(project_path)
    _set_config_paths(project_path)

    if osutil.dir_exists(project_path) and init is False:
        click.echo(click.style('[ERROR] The directory "' + project_path + '" already exists!', fg='red'))
        exit(1)
    elif osutil.dir_exists(project_path) and init is True:
        click.echo(click.style('[WARNING] The directory "' + project_path + '" already exists!', fg='yellow'))

    click.echo('Creating: ' + project_path)
    if not init:
        osutil.mkdir(project_path)
    osutil.mkdir(conf['configdir'])
    osutil.mkdir(conf['cachedir'])
    # osutil.mkdir(project_path + '/images')
    osutil.echo(project_path, dst=conf['last'])
    osutil.echo('', dst=conf['firstfun'])

@cli.command('open')
@click.argument('project_path')
@click.option('-d', '--detach', is_flag=True, help="Detach darktable into it's own process",)
@click.option('--darktable', type=str, help="/path/to/command (command if in PATH)", default='darktable')
@click.option('--use-flatpak', is_flag=True, help="Use the Darktable flatpak. Ignores --darktable")
def open_project(darktable, project_path, detach=False, use_flatpak=False):
    """Open an existing project"""

    # Check if darktable is runnable before modifying the project library
    if use_flatpak is True:
        darktable = 'org.darktable.Darktable'

    which_darktable = shutil.which(darktable)

    if which_darktable is None:
        click.secho('[ERROR] "' + darktable + '" not found!', fg='red')
        exit(1)

    project_path = _format_path(project_path)
    _set_config_paths(project_path)

    if not osutil.file_exists(conf['last']):
        click.echo(click.style('[ERROR] "' + conf['last'] + '" dose not exist!', fg='red'))
        exit(1)

    # Vars
    last_location = osutil.cat(conf['last'])
    current_location = project_path
    library = conf['librarydb']
    firstrun = conf['firstfun']

    # Check if the darktable library exists.
    # It may not exist if the project was just created and darktable has not yet been open.
    # This is just a check.
    if osutil.file_exists(library):
        click.echo(click.style('Found: "' + library + '"', fg='green'))
    else:
        click.secho('[WARNING] "' + library + '" does not exist!\n'
                    '          This most likely means that darktable hasn\'t been initialized yet.',
                    fg='yellow')

    # Check if this is the first time opening the project.
    if not osutil.file_exists(firstrun):
        # Check to see if the project has moved
        if last_location != current_location:
            click.echo(click.style('[WARNING] It looks like the project has moved', fg='yellow'))
            _update_base_path(library, last_location, current_location)
        else:
            click.echo('Locations match')

    _launch_dt(which_darktable, detach)


if __name__ == '__main__':
    cli()