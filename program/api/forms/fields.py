from django.forms.fields import ChoiceField, Field
from django.forms.models import ModelChoiceIterator as MCIter
from django.forms.models import ModelChoiceField as MCField
from django.core.exceptions import (
    NON_FIELD_ERRORS, FieldError, ImproperlyConfigured, ValidationError,
)
from django.forms.widgets import (
    HiddenInput, MultipleHiddenInput, RadioSelect, SelectMultiple,
)

class ModelChoiceIterator(MCIter):
    def __init__(self, field):
        self.field = field
        self.queryset = field.values

    def __iter__(self):
        if self.field.empty_label is not None:
            yield ("", self.field.empty_label)
        queryset = self.queryset
        print(queryset)
        for obj in queryset:
            yield self.choice(obj)

    def choice(self, obj):
        print(obj)
        return (
            self.field.prepare_value(obj),
            self.field.label_from_instance(obj),
        )

class ModelChoiceField(MCField):
    iterator = ModelChoiceIterator

    def _get_queryset(self):
        return self._queryset

    def _set_queryset(self, queryset):
        print("SETTING QUERYSET")
        self._queryset = None if queryset is None else queryset.all()
        self.values = self._queryset.all_values()
        self.widget.choices = self.choices

    queryset = property(_get_queryset, _set_queryset)

    def label_from_instance(self, obj):
        return obj["__str__"]

    choices = property(MCField._get_choices, ChoiceField._set_choices)

    def prepare_value(self, obj):
        if obj:
            return obj["id"]

    def to_python(self, value):
        if value in self.empty_values:
            return None
        try:
            key = self.to_field_name or 'pk'
            if isinstance(value, self.queryset.model):
                value = getattr(value, key)
            value = self.queryset.get(**{key: value})
        except (ValueError, TypeError, self.queryset.model.DoesNotExist):
            raise ValidationError(self.error_messages['invalid_choice'], code='invalid_choice')
        return value

    def validate(self, value):
        return Field.validate(self, value)

    def has_changed(self, initial, data):
        if self.disabled:
            return False
        initial_value = initial if initial is not None else ''
        data_value = data if data is not None else ''
        return str(self.prepare_value(initial_value)) != str(data_value)

