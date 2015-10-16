# -*- coding: utf-8 -*-
import click
import logging
import os

from cleanit import api
from cleanit.config import Config
from cleanit.subtitle import Subtitle


logger = logging.getLogger('cleanit')


@click.command()
@click.option('-c', '--config', help='YAML config file to be used')
@click.option('-f', '--force', is_flag=True, default=False,
              help='Force saving the subtitle even if there was no change.')
@click.option('--test', is_flag=True, help='Do not make any change. Useful to be used together with --debug')
@click.option('--debug', is_flag=True, help='Print useful information for debugging and for reporting bugs.')
@click.option('-v', '--verbose', count=True, help='Display debug messages')
@click.argument('path', type=click.Path(), required=True, nargs=-1)
def cleanit(config, force, test, debug, verbose, path):
    if debug:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(logging.BASIC_FORMAT))
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)

    cfg = Config.from_file(config)

    collected_subtitles = []
    discarded_paths = []

    for p in path:
        scan(p, collected_subtitles, discarded_paths)

    if verbose and discarded_paths:
        click.echo('Discarded %s' % discarded_paths, color='red')

    click.echo('Collected %d subtitles' % len(collected_subtitles), color='green')
    for sub in collected_subtitles:
        modified = api.clean_subtitle(sub, cfg.rules)
        if (modified or force) and not test:
            click.echo("Saving '%s'" % sub.path, color='green')
            api.save_subtitle(sub)
            click.echo("Saved '%s'" % sub.path, color='green')
        elif verbose > 0:
            click.echo("No modification for '%s'" % sub.path, color='green')


def scan(path, collected, discarded):
    if not os.path.exists(path):
        discarded.append(path)

    elif os.path.isfile(path):
        if path.lower().endswith('.srt'):
            collected.append(Subtitle(path))

    elif os.path.isdir(path):
        for dir_path, dir_names, file_names in os.walk(path):
            for filename in file_names:
                file_path = os.path.join(dir_path, filename)
                scan(file_path, collected, discarded)
