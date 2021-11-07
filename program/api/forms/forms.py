from django.db.models.fields.related import ForeignKey
from django.forms import ModelForm
from django.forms.forms import BaseForm, DeclarativeFieldsMetaclass
from django.forms import ALL_FIELDS, BaseModelFormSet
from django.forms.models import apply_limit_choices_to_to_formfield, ModelFormOptions
from django.core.exceptions import (
    NON_FIELD_ERRORS, FieldError, ImproperlyConfigured, ValidationError,
)
from itertools import chain
from django.forms import CharField
from django.forms.utils import ErrorList
from program.api.forms.fields import ModelChoiceField

def fields_for_model(model, fields=None, exclude=None, widgets=None,
                     formfield_callback=None, localized_fields=None,
                     labels=None, help_texts=None, error_messages=None,
                     field_classes=None, *, apply_limit_choices_to=True):
    field_dict = {}
    ignored = []
    opts = model._meta
    # Avoid circular import
    from django.db.models import Field as ModelField
    sortable_private_fields = [f for f in opts.private_fields if isinstance(f, ModelField)]
    for f in sorted(chain(opts.concrete_fields, sortable_private_fields, opts.many_to_many)):
        if not getattr(f, 'editable', False):
            if (fields is not None and f.name in fields and
                    (exclude is None or f.name not in exclude)):
                raise FieldError(
                    "'%s' cannot be specified for %s model form as it is a non-editable field" % (
                        f.name, model.__name__)
                )
            continue
        if fields is not None and f.name not in fields:
            continue
        if exclude and f.name in exclude:
            continue

        kwargs = {}
        if widgets and f.name in widgets:
            kwargs['widget'] = widgets[f.name]
        if localized_fields == ALL_FIELDS or (localized_fields and f.name in localized_fields):
            kwargs['localize'] = True
        if labels and f.name in labels:
            kwargs['label'] = labels[f.name]
        if help_texts and f.name in help_texts:
            kwargs['help_text'] = help_texts[f.name]
        if error_messages and f.name in error_messages:
            kwargs['error_messages'] = error_messages[f.name]
        if field_classes and f.name in field_classes:
            kwargs['form_class'] = field_classes[f.name]
        if formfield_callback is None:
            formfield = f.formfield(**kwargs)
        elif not callable(formfield_callback):
            raise TypeError('formfield_callback must be a function or callable')
        else:
            formfield = formfield_callback(f, **kwargs)

        if formfield:
            if apply_limit_choices_to:
                apply_limit_choices_to_to_formfield(formfield)
            field_dict[f.name] = formfield
        else:
            ignored.append(f.name)
    if fields:
        # filter field_dict
        field_dict = {
            f: field_dict.get(f) for f in fields
            if (not exclude or f not in exclude) and f not in ignored 
        }
        # add value fileds (Charfields) to None fields
        for f, v in field_dict.items():
            if not v:
                field_dict[f] = CharField(disabled=True)
    return field_dict

def model_to_dict(instance,values, fields=None, exclude=None):
    data = {}
    if values:
        for field in fields:
            data[field] = values.get(field)
    else:
        try:
            values = instance.all_values()
            data = model_to_dict(instance,values,fields,exclude)
        except:
            opts = instance._meta
            for f in chain(opts.concrete_fields, opts.private_fields, opts.many_to_many):
                if not getattr(f, 'editable', False):
                    continue
                if fields is not None and f.name not in fields:
                    continue
                if exclude and f.name in exclude:
                    continue
                data[f.name] = f.value_from_object(instance)
    return data

def field_callback(field,**kwargs):
    if isinstance(field, ForeignKey):
        f = field.formfield(form_class=ModelChoiceField, **kwargs)
        return f
    else:
        return field.formfield(**kwargs)

class ModelFormMetaclass(DeclarativeFieldsMetaclass):
    def check_bases(self,bases):
        return bases == (BaseModelForm,)

    def __new__(mcs, name, bases, attrs):
        base_formfield_callback = field_callback
        for b in bases:
            if hasattr(b, 'Meta') and hasattr(b.Meta, 'formfield_callback'):
                base_formfield_callback = b.Meta.formfield_callback
                break

        formfield_callback = attrs.pop('formfield_callback', base_formfield_callback)

        new_class = super().__new__(mcs, name, bases, attrs)

        if new_class.check_bases(bases):
            return new_class

        opts = new_class._meta = ModelFormOptions(getattr(new_class, 'Meta', None))

        # We check if a string was passed to `fields` or `exclude`,
        # which is likely to be a mistake where the user typed ('foo') instead
        # of ('foo',)
        for opt in ['fields', 'exclude', 'localized_fields']:
            value = getattr(opts, opt)
            if isinstance(value, str) and value != ALL_FIELDS:
                msg = ("%(model)s.Meta.%(opt)s cannot be a string. "
                       "Did you mean to type: ('%(value)s',)?" % {
                           'model': new_class.__name__,
                           'opt': opt,
                           'value': value,
                       })
                raise TypeError(msg)

        if opts.model:
            # If a model is defined, extract form fields from it.
            if opts.fields is None and opts.exclude is None:
                raise ImproperlyConfigured(
                    "Creating a ModelForm without either the 'fields' attribute "
                    "or the 'exclude' attribute is prohibited; form %s "
                    "needs updating." % name
                )

            if opts.fields == ALL_FIELDS:
                # Sentinel for fields_for_model to indicate "get the list of
                # fields from the model"
                opts.fields = None

            fields = fields_for_model(
                opts.model, opts.fields, opts.exclude, opts.widgets,
                formfield_callback, opts.localized_fields, opts.labels,
                opts.help_texts, opts.error_messages, opts.field_classes,
                # limit_choices_to will be applied during ModelForm.__init__().
                apply_limit_choices_to=False,
            )
            # Override default model fields with any custom declared ones
            # (plus, include all the other declared fields).
            fields.update(new_class.declared_fields)
        else:
            fields = new_class.declared_fields
        new_class.base_fields = fields

        editable_fields = []
        for formfield in fields.values():
            if not formfield.disabled:
                editable_fields.append(formfield)
        new_class.editable_fields = editable_fields
        return new_class

class BaseModelForm(BaseForm):
    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None,
                 initial=None, error_class=ErrorList, label_suffix=None,
                 empty_permitted=False, instance=None, values=None, use_required_attribute=None,
                 renderer=None):
        opts = self._meta
        if opts.model is None:
            raise ValueError('ModelForm has no model class specified.')
        if instance is None:
            # if we didn't get an instance, instantiate a new one
            self.instance = opts.model()
            object_data = {}
        else:
            self.instance = instance
            if not values:
                self.values = self.instance.all_values()
            else:
                self.values = values
            object_data = model_to_dict(self.instance, self.values, opts.fields, opts.exclude)
        # if initial was provided, it should override the values from instance
        if initial is not None:
            object_data.update(initial)
        # self._validate_unique will be set to True by BaseModelForm.clean().
        # It is False by default so overriding self.clean() and failing to call
        # super will stop validate_unique from being called.
        self._validate_unique = False
        super().__init__(
            data, files, auto_id, prefix, object_data, error_class,
            label_suffix, empty_permitted, use_required_attribute=use_required_attribute,
            renderer=renderer,
        )
        for formfield in self.fields.values():
            apply_limit_choices_to_to_formfield(formfield)
        
class ModelForm(BaseModelForm,metaclass=ModelFormMetaclass):
    pass

class ExtendedModelFormMetaclass(ModelFormMetaclass):
    def check_bases(self,bases):
        return bases == (ModelForm,)

class RowModelForm(ModelForm):
    pass

class ViewModelForm(ModelForm):
    pass

class ViewOnlyModelForm(ViewModelForm):
    pass
