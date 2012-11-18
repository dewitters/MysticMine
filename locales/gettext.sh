#/usr/bin/env bash

xgettext --language=python --copyright-holder='Koonsolo' --package-name='monorail' --package-version='1.0.0' --msgid-bugs-address='koen@koonsolo.com' -d monorail -o messages.pot ../source/*.py ../source_demo/*.py

msginit --locale=ru_RU -o ru_RU.po
msginit --locale=en_US -o en_US.po


# msgfmt -o locale/ru_RU/LC_MESSAGES/monorail.mo ru_RU.po
