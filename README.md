# Конвертация контента с сайта articulus.elibrary.ru в штатный XML для импорта
При вызове без параметров исходные файлы должны лежать в каталоге **IDATA**

Так же при работе используется каталог для временных файлов.

После работы создаётся выходной файл с именем вида `CODNEB_DATE_unicode.xml`,
где *CODNEB* - код НЭБ а *DATE* - текущая дата

Вызов программы:
```bash
$ convert --help
Usage: convert.py [OPTIONS]

Options:
  -i, --input-dir PATH            Путь к каталогу с сохранёнными файлами
                                  [default: IDATA]
  -o, --out-name PATH             Имя выходного файла. Для вывода в
                                  стандартный поток используйте "-" [по
                                  умолчанию CODNEB_DATE_unicode.xml]
  --out-dir PATH                  Путь к каталогу выходного файла [по
                                  умолчанию текущий]
  --codeNEB TEXT                  codeNEB если он отличается от issn
  --temp-path PATH                Путь к каталогу для временных файлов. Для
                                  использования системного укажите "-"
                                  [default: JORNAL-TMP]
  --validation / --no-validation  Проверка сгенерированного XML-я  [default:
                                  True]
  -l, --log PATH                  Имя лог-файла. Для вывода в стандартный
                                  поток ошибок используйте "-"   [default:
                                  convert.log]
  -v, --verbose                   Подробная информация в логе
  -q, --quiet                     Краткая информация в логе [по умолчанию]
  --silent                        Только ошибки в логе
  --debug                         Отладочная информация в логе
  --no-console                    Отключить вывод в консоль
  --help                          Show this message and exit.

```
