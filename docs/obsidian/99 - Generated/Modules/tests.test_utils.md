---
type: module
generated: true
language: python
layer: test
qualified_name: tests.test_utils
source: tests/test_utils.py
status: active
tags: [module, test]
---

# tests.test_utils

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Source

`tests/test_utils.py`

## Imports

- `EMAIL_CATEGORIES` ← `config.settings.EMAIL_CATEGORIES`
- `PRIORITY_LEVELS` ← `config.settings.PRIORITY_LEVELS`
- `Path` ← `pathlib.Path`
- `datetime` ← `datetime.datetime`
- `extract_domain` ← `src.utils.extract_domain`
- `format_timestamp` ← `src.utils.format_timestamp`
- `get_category_emoji` ← `src.utils.get_category_emoji`
- `get_email_preview` ← `src.utils.get_email_preview`
- `get_priority_color` ← `src.utils.get_priority_color`
- `get_sender_initials` ← `src.utils.get_sender_initials`
- `pytest` ← `pytest`
- `sys` ← `sys`

## Classes

- [[tests.test_utils.TestConfiguration|TestConfiguration]]
- [[tests.test_utils.TestUtilityFunctions|TestUtilityFunctions]]

## Tests

- [[tests.test_utils.TestConfiguration.test_email_categories_exist|test_email_categories_exist]]
- [[tests.test_utils.TestConfiguration.test_priority_levels_exist|test_priority_levels_exist]]
- [[tests.test_utils.TestConfiguration.test_priority_levels_order|test_priority_levels_order]]
- [[tests.test_utils.TestUtilityFunctions.test_extract_domain|test_extract_domain]]
- [[tests.test_utils.TestUtilityFunctions.test_format_timestamp|test_format_timestamp]]
- [[tests.test_utils.TestUtilityFunctions.test_get_category_emoji|test_get_category_emoji]]
- [[tests.test_utils.TestUtilityFunctions.test_get_email_preview|test_get_email_preview]]
- [[tests.test_utils.TestUtilityFunctions.test_get_priority_color|test_get_priority_color]]
- [[tests.test_utils.TestUtilityFunctions.test_get_sender_initials|test_get_sender_initials]]
