# -*- codong: utf-8 -*-
from datetime import datetime
import logging
from pathlib import Path
from tempfile import gettempdir

from lxml import etree
from natsort import natsort_keygen


def construct_dir_source(dir_name, tmp_dir):
  # self_path = Path(__file__)
  self_path = Path('.')
  root = etree.Element('files')
  parser = etree.HTMLParser()
  if not tmp_dir or tmp_dir == '-':
    tmp_dir = gettempdir()
  tmp_dir = Path(tmp_dir)
  title_exists = False
  files = tuple(sorted(
    (f for f in Path(dir_name).glob('*.html') if f.is_file()),
    key=natsort_keygen()))
  for fparh in files:
    tfile:Path = tmp_dir / fparh.name
    with tfile.open('wb') as fout:
      src_root = etree.parse(fparh.as_posix(), parser)
      fout.write(
        etree.tostring(src_root, pretty_print=True, encoding='utf-8'))
    if fparh.name.lower() == 'title.html':
      title_exists = True
      tag = 'title'
    else:
      tag = 'issue'
    file_uri = tfile.as_uri() if tfile.is_absolute() else tfile.as_posix()
    etree.SubElement(root, tag, path=file_uri)
  logging.debug(etree.tostring(root, pretty_print=True, encoding='unicode'))
  if not title_exists:
    logging.error(
      'В составе файлов не обнаружили title.html: %s',
      tuple(f.resolve().as_posix() for f in  files))
    raise SystemExit(1)
  return root


def soran_transform_dir(
  dir_name, oname:str, out_dir:str, codeNEB:str, temp_path:str
):
  src_root = construct_dir_source(dir_name, temp_path)

  ns = etree.FunctionNamespace('http://promsoft.ru/soran_transform/dir')
  ns.prefix = 'ps'

  journal = JornalParser(ns)

  parser = etree.XMLParser(no_network=True)
  parser.resolvers.add(FileResolver())

  # xslt = etree.XML(XSLT, parser)
  xslt = etree.parse('convert_dir.xslt', parser)
  transform = etree.XSLT(xslt)
  parser = etree.HTMLParser()
  # src_root = etree.parse(iname, parser)
  # res_trans = transform(src_root, params=etree.XSLT.strparam(openstat))
  res_trans = transform(src_root)
  if oname == '-':
    print(res_trans)
    return

  if not oname:
    if not codeNEB:
      codeNEB = journal.codeNEB
    oname = f'{codeNEB}_{datetime.now().date().isoformat()}_unicode.xml'
  opath = Path(out_dir) / oname if out_dir else Path(oname)
  with opath.open('wt', encoding='utf-8') as out:
    out.write('%s' % res_trans)

  logging.info('Создан файл: %s', opath)

  return opath


class FileResolver(etree.Resolver):
  def resolve(self, url, pubid, context):
    # print(url)
    return self.resolve_filename(url, context)


class JornalParser:

  codeNEB:str = None

  def __init__(self, ns):
    ns['get_pid'] = self.get_pid
    ns['get_codeNEB'] = self.get_codeNEB
    ns['ends-with'] = self.ends_with
    ns['now'] = self.now

  def get_pid(self, _, e):
    tid = e[0].text.split()[1]
    return tid

  def get_codeNEB(self, _, e):
    issn = e[0].text.strip()
    self.codeNEB = codeNEB = ''.join(c for c in issn if c.isdigit())
    return codeNEB

  def ends_with(self, _, s, *args):
    if not s:
      return False
    if not isinstance(s, str):
      s = s[0]
    return s.endswith(args)

  def now(self, _):
    dt = datetime.now().replace(microsecond=0)
    return dt.isoformat(' ')
