#/usr/bin/env bash
# Generate messages.pot

xgettext --language=python --copyright-holder='Koonsolo' --package-name='monorail' --package-version='1.0.0' --msgid-bugs-address='koen@koonsolo.com' -d monorail -o messages.pot ../monorail/*.py

# Examples to create your own locale file
#
# msginit --locale=ru_RU -o ru_RU.po
# msginit --locale=en_US -o en_US.po
# msgfmt -o locale/ru_RU/LC_MESSAGES/monorail.mo ru_RU.po
