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


JOURNAL_TMP = 'JOURNAL-TMP'

def validate_tmps(ctx, param, value):
  pass


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
  '-t', '--title-name', default='title.html', show_default=True,
  help='Имя файла с общей снформацией о выпуске')
@click.option(
  '--temp-path', default=JOURNAL_TMP, show_default=True,
  type=click.Path(dir_okay=True, writable=True, allow_dash=True),
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
@click.option('--no-console', is_flag=True, help='Отключить вывод в консоль')
def main(
  validation:bool, input_dir:str, out_name:str, codeneb:str, title_name:str,
  out_dir:str, temp_path:str, log:str, log_level:str, no_console:bool
):
  _init_logging(log, log_level, no_console)

  logging.debug('validation: %s', validation)
  logging.debug('input_dir: %s', input_dir)
  logging.debug('out_file: %s', out_name)
  logging.debug('codeNEB: %s', codeneb)
  logging.debug('title_name: %s', title_name)
  logging.debug('out_dir: %s', out_dir)
  logging.debug('temp_path: %s:', temp_path)
  # return

  # soran_transform_page('data.html', 'data.xml')
  out_file = soran_transform_dir(
    Path(input_dir), out_name, out_dir, codeneb, title_name, temp_path)

  if validation and out_file:
    relaxng = create_validator()
    out = etree.parse(out_file.as_posix())
    if not relaxng.validate(out):
      for ell in relaxng.error_log:
        logging.warning(ell)
        raise SystemExit(2)
    else:
      logging.info('Созданный файл %s валиден', out_file)


def _init_logging(log, log_level, no_console):
  kwds = {}
  if not log or log == '-':
    kwds.update(stream=None)
    to_console = True
  else:
    kwds.update(filename=log)
    to_console = False
  level = log_level or logging.WARN
  format = '%(asctime)s %(levelname)-8s %(module)-15s:%(lineno)d %(message)s'
  logging.basicConfig(
    format=format,
    level=level, **kwds)
  if no_console or to_console:
    return

  # define a Handler which writes INFO messages or higher to the sys.stderr
  console = logging.StreamHandler()
  console.setLevel(level) # if level not in {'INFO', 'DEBUG'} else 'INFO')  # logging.INFO) #DEBUG) #
  formatter = logging.Formatter(fmt=format)  # , datefmt=datefmt)
  console.setFormatter(formatter)
  logging.getLogger('').addHandler(console)


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
  # rng_tree = rnc2rng.load('articles.rnc')
  rng_tree = rnc2rng.loads(ARTICLES_RNC)
  # print(rnc2rng.dumps(rng_tree))
  rng_str = rnc2rng.dumps(rng_tree)
  # print(rng_str[:100])
  rng_doc = etree.parse(BytesIO(rng_str.encode('utf-8')))
  relaxng = etree.RelaxNG(rng_doc)
  return relaxng


# language=RELAX-NG
ARTICLES_RNC = '''
default namespace = ""

start =
    element journal {
        element operCard {
            element operator { xsd:NCName },
            element pid { xsd:integer },
            element date { text },
            element cntArticle { xsd:integer },
            element cntNode { empty },
            element cs { xsd:integer }
        },
        element titleid { xsd:integer },
        element issn { xsd:NMTOKEN },
        element codeNEB { xsd:integer }?,
        element journalInfo {
            attribute lang { xsd:NCName },
            element title { text }
        },
        element issue {
            element volume { xsd:integer | empty },
            element number { xsd:integer },
            element altNumber { empty },
            element part { empty },
            element dateUni { text },
            element issTitle { empty },
            pages,
            element articles {
                (element section {
                    element secTitle {
                        attribute lang { xsd:NCName },
                        text
                    }+
                }?,
                element article {
                    pages,
                    element artType { xsd:NCName },
                    element authors {
                        element author {
                            attribute num { xsd:integer },
                            element individInfo {
                                attribute lang { xsd:NCName },
                                element surname { text },
                                element initials { text },
                                (element address { text }
                                 & element email { text }?
                                 & element orgName { text }?)?
                            }+
                        }+
                    },
                    element artTitles {
                        element artTitle {
                            attribute lang { xsd:NCName },
                            (text
                             | element i {text} )+
                        }+
                    },
                    element abstracts {
                        element abstract {
                            attribute lang { xsd:NCName },
                            (text
                             | element sub { text }
                             | element sup { text }
                             | element i {text} )+
                        }+
                    },
                    element text {
                        attribute lang { xsd:NCName },
                        text
                    },
                    element codes {
                        element udk { text },
                        element doi { text }?
                    },
                    element keywords {
                        element kwdGroup {
                            attribute lang { xsd:NCName },
                            element keyword { text }+
                        }
                    },
                    element references {
                        element reference { text }+
                    },
                    (element artFunding {
                          element funding {
                              attribute lang { xsd:NCName },
                              text
                          }
                    }? &
                    element dates {
                            element dateReceived { xsd:NMTOKEN }
                    }? &
                    element files {
                        element file { text }
                    }? )
                })+
            }
        }
    }
pages = element pages { xsd:NMTOKEN }
'''


if __name__ == '__main__':
  main()
