# juntagrico-custom_sub

[![juntagrico-ci](https://github.com/juntagrico/juntagrico-custom-sub/actions/workflows/juntagrico-ci.yml/badge.svg?branch=main&event=push)](https://github.com/juntagrico/juntagrico-custom-sub/actions/workflows/juntagrico-ci.yml)
[![Maintainability](https://api.codeclimate.com/v1/badges/562e49b1e35490ac4058/maintainability)](https://codeclimate.com/github/juntagrico/juntagrico-custom-sub/maintainability)
[![Test Coverage](https://api.codeclimate.com/v1/badges/562e49b1e35490ac4058/test_coverage)](https://codeclimate.com/github/juntagrico/juntagrico-custom-sub/test_coverage)
[![image](https://img.shields.io/github/last-commit/juntagrico/juntagrico-custom-sub.svg)](https://github.com/juntagrico/juntagrico-custom-sub)
[![image](https://img.shields.io/github/commit-activity/y/juntagrico/juntagrico-custom-sub)](https://github.com/juntagrico/juntagrico-custom-sub)

This is an extension for juntagrico. You can find more information about juntagrico here (https://github.com/juntagrico/juntagrico).

This extension provides support for custom composition of subscriptions.
Each user can select the amount of predefined products in his or her subscription.
A subscription has a total amount of available units and each product can be assigned a size in these units.

The extension also creates depot lists and packing lists that describe which products should be delivered to a depot and by which user they should be collected.

## Installation


Install juntagrico-badge via `pip`

    $ pip install juntagrico-custom-sub

or add it in your projects `requirements.txt`

In `settings.py` add `'juntagrico_custom_sub',`, *above* `'juntagrico'`.

```python
INSTALLED_APPS = [
    ...
    'juntagrico_custom_sub',
    'juntagrico',
]
```

In your `urls.py` you also need to extend the pattern:

```python
urlpatterns = [
    ...
    path('', include('juntagrico_custom_sub.urls')),
]
```
