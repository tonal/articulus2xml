#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
"""
from io import BytesIO
import logging
from pathlib import Path

import click
from lxml import etree
import rnc2rng

from convert_dir import soran_transform_dir
# from convert_page import soran_transform_page


JORNAL_TMP = Path('JORNAL-TMP')


@click.command()
@click.option(
  '-i', '--input-dir',
  type=click.Path(exists=True, dir_okay=True, readable=True),
  default='IDATA', show_default=True,
  help='Путь к каталогу с сохранёнными файлами')
@click.option(
  '-o', '--out-name',
  type=click.Path(file_okay=True, writable=True, allow_dash=True),
  help='Имя выходного файла. Для вывода в стандартный поток используйте "-" [по умолчанию CODNEB_DATE_unicode.xml]')
@click.option(
  '--out-dir',
  type=click.Path(exists=True, dir_okay=True, writable=True),
  help='Путь к каталогу выходного файла [по умолчанию текущий]' )
@click.option('--codeNEB', help='codeNEB если он отличается от issn')
@click.option(
  '--temp-path', default=JORNAL_TMP, show_default=True,
  type=click.Path(exists=True, dir_okay=True, writable=True, allow_dash=True),
  help='Путь к каталогу для временных файлов. Для использования системного укажите "-"'
)
@click.option(
  '--validation/--no-validation', default=True, show_default=True,
  help='Проверка сгенерированного XML-я')
@click.option(
  '-l', '--log', default='convert.log', show_default=True,
  type=click.Path(file_okay=True, writable=True, allow_dash=True),
  help='Имя лог-файла. Для вывода в стандартный поток ошибок используйте "-" '
  )
@click.option(
  '-v', '--verbose', 'log_level', flag_value='INFO',
  help='Подробная информация в логе')
@click.option(
  '-q', '--quiet', 'log_level', flag_value='WARNING',
  help='Краткая информация в логе [по умолчанию]')
@click.option(
  '--silent', 'log_level', flag_value='ERROR',
  help='Только ошибки в логе')
@click.option(
  '--debug', 'log_level', flag_value='DEBUG',
  help='Отладочная информация в логе')
def main(
  validation:bool, input_dir:str, out_name:str, codeneb:str, out_dir:str,
  temp_path:str, log:str, log_level:str
):
  kwds = {}
  if not log or log == '-':
    kwds.update(stream=None)
  else:
    kwds.update(filename=log)
  logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(module)-15s:%(lineno)d %(message)s',
    level=log_level or logging.WARN, **kwds)

  logging.debug('validation: %s', validation)
  logging.debug('input_dir: %s', input_dir)
  logging.debug('out_file: %s', out_name)
  logging.debug('codeNEB: %s', codeneb)
  logging.debug('out_dir: %s', out_dir)
  logging.debug('temp_path: %s:', temp_path)
  # return

  # soran_transform_page('data.html', 'data.xml')
  out_file = soran_transform_dir(
    input_dir, out_name, out_dir, codeneb, temp_path)
  logging.debug('Создан файл: %s', out_file)

  if validation and out_file:
    relaxng = create_validator()
    out = etree.parse(out_file.as_posix())
    if not relaxng.validate(out):
      for ell in relaxng.error_log:
        logging.warning(ell)
    else:
      logging.info('Созданный файл %s валиден', out_file)


def validate_all_xml(relaxng):
  cnt = 0
  for p_xml in sorted(Path('.').glob('*.xml')):
    if p_xml.name == 'OAO_32_05_2019_new.xml':
      continue
    doc = etree.parse(p_xml.as_posix())
    if not relaxng.validate(doc):
      print(p_xml)
      for ell in relaxng.error_log:
        print(ell)
      print()
  print(cnt)


def create_validator():
  rng_tree = rnc2rng.load('articles.rnc')
  # print(rnc2rng.dumps(rng_tree))
  rng_str = rnc2rng.dumps(rng_tree)
  # print(rng_str[:100])
  rng_doc = etree.parse(BytesIO(rng_str.encode('utf-8')))
  relaxng = etree.RelaxNG(rng_doc)
  return relaxng


if __name__ == '__main__':
  main()
