# -*- coding: utf-8 -*-
from typing import List, Tuple, Set, Optional

import click
import logging
import os

from babelfish import Error as BabelfishError, Language

from cleanit.config import Config
from cleanit.rule import Rules
from cleanit.subtitle import Subtitle


logger = logging.getLogger('cleanit')


class LanguageParamType(click.ParamType):
    name = 'language'

    def convert(self, value, param, ctx):
        try:
            return Language.fromietf(value)
        except (BabelfishError, ValueError):
            self.fail(f"{click.style(f'{value}', bold=True)} is not a valid language")


LANGUAGE = LanguageParamType()


@click.command()
@click.option('-c', '--config', type=click.Path(), help='YAML config file to be used')
@click.option('-l', '--language', type=LANGUAGE, multiple=True, help='Language as IETF code, '
              'e.g. en, pt-BR (can be used multiple times).')
@click.option('-t', '--tag', required=True, multiple=True, help='Rule tags to be used, '
              'e.g. ocr, tidy, no-sdh, no-style, no-lyrics, no-spam (can be used multiple times). ')
@click.option('-e', '--encoding', help='Save subtitles using the following encoding.')
@click.option('-f', '--force', is_flag=True, default=False,
              help='Force saving the subtitle even if there was no change.')
@click.option('--test', is_flag=True, help='Do not make any change. Useful to be used together with --debug')
@click.option('--debug', is_flag=True, help='Print useful information for debugging and for reporting bugs.')
@click.option('-v', '--verbose', count=True, help='Display debug messages')
@click.argument('path', type=click.Path(), required=True, nargs=-1)
def cleanit(config: Optional[str], language: Optional[Tuple[Language]], tag: Tuple[str],
            encoding: Optional[str],
            force: bool, test: bool, debug: bool, verbose: int, path: Tuple[str]):
    if debug:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(logging.BASIC_FORMAT))
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)

    languages = set(language)
    tags = set(tag)

    if config and (not os.path.isfile(config) or os.path.isdir(config)):
        click.echo(f"Invalid configuration is defined: {click.style(config, bold=True)}")
        return

    cfg = Config.from_path(config)

    rules = cfg.select_rules(tags=tags, languages=languages)
    if not rules:
        click.echo(f"No rules defined for "
                   f"{click.style(', '.join(tag + tuple(str(lang) for lang in languages)), bold=True)}")
        return

    collected_subtitles: List[Subtitle] = []
    filtered_out_paths: List[str] = []
    discarded_paths: List[str] = []

    if debug or verbose > 1:
        for p in path:
            scan(p, languages, collected_subtitles, filtered_out_paths, discarded_paths)
    else:
        with click.progressbar(path, label='Collecting subtitles', item_show_func=lambda item: item or '') as bar:
            for p in bar:
                scan(p, languages, collected_subtitles, filtered_out_paths, discarded_paths)

    if debug or verbose > 1:
        if verbose > 2:
            for p in filtered_out_paths:
                click.echo(f"{click.style(p, fg='yellow', bold=True)} filtered out")
        for p in discarded_paths:
            click.echo(f"{click.style(p, fg='red', bold=True)} discarded")

    # report collected subtitles
    click.echo(f"{click.style(str(len(collected_subtitles)), bold=True, fg='green')} "
               f"subtitle{'s' if len(collected_subtitles) > 1 else ''} collected / "
               f"{click.style(str(len(filtered_out_paths)), bold=True, fg='yellow')} "
               f"subtitle{'s' if len(filtered_out_paths) > 1 else ''} filtered out / "
               f"{click.style(str(len(discarded_paths)), bold=True, fg='red')} "
               f"path{'s' if len(discarded_paths) > 1 else ''} ignored")

    if not collected_subtitles:
        return

    if debug or verbose > 1:
        for sub in collected_subtitles:
            clean_subtitle(sub, rules, encoding, force, test, verbose)
    else:
        saved_count = 0
        with click.progressbar(collected_subtitles, label='Cleaning subtitles',
                               item_show_func=lambda s: click.style(s and s.name or '', bold=True)) as bar:
            for sub in bar:
                saved = clean_subtitle(sub, rules, encoding, force, test, verbose)
                saved_count += 1 if saved else 0

        # report processed subtitles
        unchanged_count = len(collected_subtitles) - saved_count
        click.echo(f"{click.style(str(saved_count), bold=True, fg='green')} "
                   f"subtitle{'s' if saved_count > 1 else ''} saved / "
                   f"{click.style(str(unchanged_count), bold=True, fg='yellow')} "
                   f"subtitle{'s' if unchanged_count > 1 else ''} unchanged")


def clean_subtitle(sub: Subtitle, rules: Rules, encoding: Optional[str], force: bool, test: bool, verbose: int,
                   echo=False):
    try:
        modified = sub.clean(rules)
        if (modified or force) and not test:
            sub.save(encoding=encoding)
            if echo:
                click.echo(f"{click.style(sub.name, fg='green', bold=True)} saved.")
            return True
        elif echo and verbose > 1:
            click.echo(f"No modifications for {click.style(sub.name, fg='yellow')}", )

        return False
    except Exception as e:
        logger.warning(f'Error while trying to clean {sub.name}: <{type(e).__name__}> [{e}]',
                       exc_info=logger.isEnabledFor(logging.DEBUG))
    finally:
        # to free up memory
        sub.finalize()


def scan(path: str, languages: Set[Language], collected: List[Subtitle], filtered_out: List[str], discarded: List[str]):
    if not os.path.exists(path):
        discarded.append(path)

    elif os.path.isfile(path):
        if path.lower().endswith('.srt'):
            subtitle = Subtitle(path)
            if subtitle.match(languages):
                collected.append(subtitle)
            else:
                filtered_out.append(path)

    elif os.path.isdir(path):
        for dir_path, dir_names, file_names in os.walk(path):
            for filename in file_names:
                file_path = os.path.join(dir_path, filename)
                scan(file_path, languages, collected, filtered_out, discarded)
