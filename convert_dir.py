# -*- codong: utf-8 -*-
from datetime import datetime
from pathlib import Path

from lxml import etree
from natsort import natsort_keygen

JORNAL_TMP = Path('JORNAL-TMP')

def construct_dir_source(dir_name):
  # self_path = Path(__file__)
  self_path = Path('.')
  root = etree.Element('files')
  parser = etree.HTMLParser()
  tmp_dir = JORNAL_TMP
  for fparh in sorted(Path(dir_name).glob('*.html'), key=natsort_keygen()):
    tfile = (tmp_dir / fparh.name)
    with tfile.open('wb') as fout:
      src_root = etree.parse(fparh.as_posix(), parser)
      fout.write(
        etree.tostring(src_root, pretty_print=True, encoding='utf-8'))
    tag = 'title' if fparh.name.lower() == 'title.html' else 'issue'
    etree.SubElement(
      root, tag, path=tfile.as_posix())
  return root


def soran_transform_dir(dir_name, oname):
  src_root = construct_dir_source(dir_name)
  print(etree.tostring(src_root, pretty_print=True, encoding='unicode'))
  # return
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
  open(oname, 'wt', encoding='utf-8').write('%s' % res_trans)


class FileResolver(etree.Resolver):
  def resolve(self, url, pubid, context):
    # print(url)
    return self.resolve_filename(url, context)


class JornalParser:

  root = None

  def __init__(self, ns):
    ns['get_pid'] = self.get_pid
    ns['ends-with'] = self.ends_with
    ns['now'] = self.now

  def get_pid(self, _, e):
    tid = e[0].text.split()[1]
    return tid

  def ends_with(self, _, s, *args):
    if not s:
      return False
    if not isinstance(s, str):
      s = s[0]
    return s.endswith(args)

  def now(self, _):
    dt = datetime.now().replace(microsecond=0)
    return dt.isoformat(' ')
