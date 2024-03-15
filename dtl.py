#!/usr/bin/env python3
"""A cli for creating and opening multiple Darktable libraries."""

import sqlite3
import os
import re
import subprocess
import click
import osutil

__version__ = '0.1'


conf = {}

def _set_config_paths(project_path):
    conf['configdir'] = project_path + '/.darktable'
    conf['cachedir'] = project_path + '/.darktable/cache'
    conf['librarydb'] = project_path + '/.darktable/library.db'
    conf['last'] = project_path + '/.darktable/.last_location'
    conf['firstfun'] = project_path + '/.darktable/.firstrun'

def _launch_dt(project_path, use_flatpak):
    """Launch Darktable"""

    librarydb = project_path + '/.darktable/library.db'
    cachedir = project_path + '/.darktable/cache'
    configdir = project_path + '/.darktable'

    cmd_options = '--cachedir ' + cachedir + ' --configdir ' + configdir + ' --library ' + librarydb

    flatpak_cmd = 'flatpak run --command=darktable org.darktable.Darktable ' + cmd_options
    usr_bin_cmd = 'darktable ' + cmd_options

    if not osutil.file_exists('/usr/bin/darktable') and use_flatpak is False:
        click.echo('"/usr/bin/darktable" not found. Switching to Flatpak')
        use_flatpak = True

    if use_flatpak:
        click.echo('Running: ' + flatpak_cmd)
        subprocess.call(flatpak_cmd, shell=True)
    else:
        click.echo('Running: ' + usr_bin_cmd)
        subprocess.call('darktable ' + cmd_options, shell=True)


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
    """Renames the last location.
    Taken from move_darktable_photos.py"""

    library_path = os.path.expanduser(library)
    new_dir = re.sub(r'/$', '', os.path.expanduser(new_path))
    old_dir = re.sub(r'/$', '', os.path.expanduser(old_path))

    conn = sqlite3.connect(library_path)
    cur = conn.cursor()
    ret = cur.execute("""select id, folder from film_rolls""")

    cnt = 0
    for elem in ret.fetchall():
        new_folder = elem[1].replace(old_dir, new_dir)
        cur.execute("""update film_rolls set folder='%s' where id='%s'""" %
                    (new_folder, elem[0]))
        cnt += 1

    conn.commit()

    click.echo("Renamed %s film rolls from %s to %s" % (cnt, old_dir, new_dir))


@click.group()
@click.version_option(version=__version__, message=__version__)
def cli():
    """A cli for creating and opening multiple Darktable libraries."""
    pass

@cli.command('create')
@click.argument('project_path')
def new_project(project_path):
    """Create a new project."""

    project_path = _format_path(project_path)
    _set_config_paths(project_path)

    if osutil.dir_exists(project_path):
        click.echo(click.style('[ERROR] The directory "' + project_path + '" already exists!', fg='red'))
        exit(1)
    else:
        click.echo('Creating: ' + project_path)
        osutil.mkdir(project_path)
        osutil.mkdir(conf['configdir'])
        osutil.mkdir(conf['cachedir'])
        # osutil.mkdir(project_path + '/images')
        osutil.echo(project_path, dst=conf['last'])
        osutil.echo('', dst=conf['firstfun'])

@cli.command('open')
@click.argument('project_path')
@click.option('--use-flatpak', is_flag=True, help="Use the Darktable flatpak.")
def open_project(project_path, use_flatpak):
    """Open an existing project."""

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

    _launch_dt(project_path, use_flatpak)


if __name__ == '__main__':
    cli()