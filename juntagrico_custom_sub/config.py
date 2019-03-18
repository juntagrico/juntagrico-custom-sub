from django.utils.translation import gettext as _

from django.conf import settings


class Config:
    def __init__(self):
        pass

    @staticmethod
    def vocabulary(key):
        if hasattr(settings, 'CS_VOCABULARY') and key in settings.CS_VOCABULARY:
            return settings.CS_VOCABULARY[key]
        return {
            'base_unit': _('Liter'),
            'base_unit_pl':_('Liter')
        }[key]
