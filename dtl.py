#!/usr/bin/env python3
"""A cli for creating and opening multiple Darktable libraries."""

import sqlite3
import os
import re
import subprocess
import click
import osutil

__version__ = '0.1'


def _get_old_path(library, project):
    """Returns the old location path"""

    conn = sqlite3.connect(library)
    cur = conn.cursor()
    ret = cur.execute("""select id, folder from film_rolls""")

    old_path = str(ret.fetchall()[0][1]).split(project)[0] + project
    conn.close()

    return old_path


def _rename_base_path(library, old, new):
    """Renames the last location.
    Taken from move_darktable_photos.py"""

    library_path = os.path.expanduser(library)
    new_dir = re.sub(r'/$', '', os.path.expanduser(new))
    old_dir = re.sub(r'/$', '', os.path.expanduser(old))

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


def path_processor(path):
    # If path ends with a `/`. If so remove it.
    if str(path).endswith('/'):
        path = path.rstrip('/')

    # Convert to an absolute path.
    path = os.path.abspath(path)

    return path


@click.group()
@click.version_option(version=__version__, message=__version__)
def cli():
    """A cli for creating and opening multiple Darktable libraries."""
    pass


@cli.command('open')
@click.argument('project_path')
@click.option('--use-flatpak', is_flag=True, help="Use the Darktable flatpak.")
def open_project(project_path, use_flatpak):
    """Open an existing project."""

    project_path = path_processor(project_path)
    project_name = project_path.split('/')[-1]
    library = project_path + '/.darktable/library.db'

    if not osutil.dir_exists(project_path):
        click.echo('"' + project_path + '" does not exist!')
    else:
        print(library)
        if osutil.file_exists(library):
            old_path = _get_old_path(library, project_name)

            if project_path != old_path:
                click.echo('Updating location')
                _rename_base_path(library, old_path, project_path)
            else:
                click.echo('Locations match')

    _launch_dt(project_path, use_flatpak)


@cli.command('create')
@click.argument('project_path')
def new_project(project_path):
    """Create a new project."""

    project_path = path_processor(project_path)

    if not osutil.dir_exists(project_path):
        click.echo('Creating: ' + project_path)
        osutil.mkdir(project_path)
        osutil.mkdir(project_path + '/.darktable')
        osutil.mkdir(project_path + '/.darktable/cache')
        # osutil.mkdir(project_path + '/images')
        # osutil.echo(project_path, project_path + '/.last_project_location')

    else:
        print('The directory "' + project_path + '" already exists!')
        click.echo('The directory "' + project_path + '" already exists!')


if __name__ == '__main__':
    cli()
