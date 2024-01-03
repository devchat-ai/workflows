
i18n-gen-msg:
	@echo "# Generating i18n base messages..."
	xgettext -k_i -o ./locales/base.pot --from-code=UTF-8 main.py
	@echo "# Done."

i18n-init-langs:
	@echo "# Init i18n language templates."
	@echo "- Initializing zh template..."
	msginit -i ./locales/base.pot -o ./locales/zh/base.po -l zh
	@echo "- Initializing en template..."
	msginit -i ./locales/base.pot -o ./locales/en/base.po -l en
	@echo "# Done."

i18n-update-langs:
	@echo "# Update i18n language templates."
	@echo "- Updating zh template..."
	msgmerge -U ./locales/zh/base.po ./locales/base.pot
	@echo "- Updating en template..."
	msgmerge -U ./locales/en/base.po ./locales/base.pot
	@echo "# Done."

i18n-compile:
	@echo "# Compile i18n messages."
	@echo "- Compiling zh..."
	msgfmt -o ./locales/zh/LC_MESSAGES/base.mo ./locales/zh/base.po
	@echo "# Compiling en..."
	msgfmt -o ./locales/en/LC_MESSAGES/base.mo ./locales/en/base.po
	@echo "# Done."
