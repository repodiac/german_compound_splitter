import locale
import os
import unittest
from unittest import mock
from types import SimpleNamespace

from german_compound_splitter import comp_split


class LocaleValidationTests(unittest.TestCase):
    def test_validate_accepts_bare_locale_names_supported_by_libc(self):
        accepted = {'de_DE', 'en_US'}

        def setlocale(category, name=None):
            if name is None:
                return 'original'
            if name not in accepted and name != 'original':
                raise locale.Error(name)
            return name

        with mock.patch.object(comp_split.locale, 'setlocale', side_effect=setlocale) as setlocale_mock:
            comp_split._validate_locales(['de_DE', 'en_US'])

        self.assertEqual(
            setlocale_mock.call_args_list,
            [
                mock.call(locale.LC_CTYPE),
                mock.call(locale.LC_CTYPE, 'de_DE'),
                mock.call(locale.LC_CTYPE, 'en_US'),
                mock.call(locale.LC_CTYPE, 'original'),
            ],
        )

    def test_validate_rejects_nonexistent_locale_and_restores_locale(self):
        def setlocale(category, name=None):
            if name is None:
                return 'original'
            if name == 'xx_YY.UTF-8':
                raise locale.Error(name)
            return name

        with mock.patch.object(comp_split.locale, 'setlocale', side_effect=setlocale) as setlocale_mock:
            with self.assertRaisesRegex(ValueError, "Locale 'xx_YY.UTF-8' is not installed"):
                comp_split._validate_locales(['xx_YY.UTF-8'])

        self.assertEqual(
            setlocale_mock.call_args_list[-1],
            mock.call(locale.LC_CTYPE, 'original'),
        )

    def test_iconv_probe_rejects_question_mark_fallback_and_uses_lc_all(self):
        result = SimpleNamespace(stdout='?', stderr='')
        with mock.patch.dict(os.environ, {'LC_ALL': 'C'}), \
                mock.patch.object(comp_split.subprocess, 'run', return_value=result) as run:
            with self.assertRaisesRegex(ValueError, "Locale 'de_DE' does not support"):
                comp_split._validate_iconv_locales(['de_DE'])

        self.assertEqual(run.call_args.kwargs['env']['LC_ALL'], 'de_DE')
        self.assertEqual(run.call_args.kwargs['input'], 'ä')

    def test_transliteration_overrides_existing_lc_all(self):
        result = SimpleNamespace(stdout='ae', stderr='')
        with mock.patch.dict(os.environ, {'LC_ALL': 'C'}), \
                mock.patch.object(comp_split.subprocess, 'run', return_value=result) as run:
            self.assertEqual(comp_split._transliterate_words(['ä'], 'de_DE'), ['ae'])

        self.assertEqual(run.call_args.kwargs['env']['LC_ALL'], 'de_DE')


if __name__ == '__main__':
    unittest.main()
