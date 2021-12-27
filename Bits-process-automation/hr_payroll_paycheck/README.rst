Install locale for Format language date_format '%B' in python
=============================================================


1. Check which locales are supported:
	locale -a
2. Add the locales you want (for example co):
	sudo locale-gen es_ES
	sudo locale-gen es_ES.UTF-8

3. Run this update command:
	sudo update-locale