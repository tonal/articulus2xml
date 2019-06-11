#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
"""
from io import BytesIO
from pathlib import Path

from lxml import etree
import rnc2rng

from convert_dir import soran_transform_dir
from convert_page import soran_transform_page


def main():
  relaxng = create_validator()

  # validate_all_xml(relaxng)

  # soran_transform_page('data.html', 'data.xml')
  soran_transform_dir('GGEO', 'data2.xml')

  out = etree.parse('data2.xml')
  if not relaxng.validate(out):
    for ell in relaxng.error_log:
      print(ell)
    print()


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
