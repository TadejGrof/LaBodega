from django.forms import BaseModelFormSet as DefaultBaseModelFormSet
from django.forms import modelformset_factory, BaseFormSet
from django.core.exceptions import (
    NON_FIELD_ERRORS, FieldError, ImproperlyConfigured, ValidationError,
)
from django.forms.formsets import DEFAULT_MIN_NUM, DEFAULT_MAX_NUM

from program.api.forms.forms import RowModelForm

class BaseModelFormSet(DefaultBaseModelFormSet):
    """
    A ``FormSet`` for editing a queryset and/or adding new objects to it.
    """
    model = None

    # Set of fields that must be unique among forms of this set.
    unique_fields = set()

    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None,
                 queryset=None, *, initial=None, **kwargs):
        self.queryset = queryset
        self.values = self.get_queryset().all_values()
        self.initial_extra = initial
        BaseFormSet.__init__(self,**{'data': data, 'files': files, 'auto_id': auto_id, 'prefix': prefix, **kwargs})

    def _construct_form(self, i, **kwargs):
        pk_required = i < self.initial_form_count()
        if pk_required:
            if self.is_bound:
                pk_key = '%s-%s' % (self.add_prefix(i), self.model._meta.pk.name)
                try:
                    pk = self.data[pk_key]
                except KeyError:
                    # The primary key is missing. The user may have tampered
                    # with POST data.
                    pass
                else:
                    to_python = self._get_to_python(self.model._meta.pk)
                    try:
                        pk = to_python(pk)
                    except ValidationError:
                        # The primary key exists but is an invalid value. The
                        # user may have tampered with POST data.
                        pass
                    else:
                        kwargs['instance'] = self._existing_object(pk)
            else:
                kwargs['instance'] = self.get_queryset()[i]
        elif self.initial_extra:
            # Set initial values for extra forms
            try:
                kwargs['initial'] = self.initial_extra[i - self.initial_form_count()]
            except IndexError:
                pass
        if self.values:
            kwargs["values"] = self.values[i]
        form = super()._construct_form(i, **kwargs)
        if pk_required:
            form.fields[self.model._meta.pk.name].required = True
        return form

    def get_queryset(self):
        if not hasattr(self, '_queryset'):
            if self.queryset is not None:
                qs = self.queryset
            else:
                qs = self.model._default_manager.get_queryset()

            # If the queryset isn't already ordered we need to add an
            # artificial ordering here to make sure that all formsets
            # constructed from this queryset have the same form order.
            if not qs.ordered:
                qs = qs.order_by(self.model._meta.pk.name)

            # Removed queryset limiting here. As per discussion re: #13023
            # on django-dev, max_num should not prevent existing
            # related objects/inlines from being displayed.
            self._queryset = qs
        return self._queryset


class ModelFormSetMeta(type):
    def check_bases(self,bases):
        return bases == (BaseModelFormSet,)
    
    def __new__(mcs, name, bases, attrs):
        new_class = super().__new__(mcs, name, bases, attrs)

        if new_class.check_bases(bases):
            return new_class
        
        form = attrs.get("form")

        if not form or not issubclass(form,RowModelForm):
            raise Exception("Invalid form at %s" %(name) )

        new_class.form = form
        new_class.model = form._meta.model

        edit = attrs.get("edit")
        toggle_edit = attrs.get("toggle_edit")
        if toggle_edit: edit = True

        if len(form.editable_fields) > 0:
            if not edit:
                for field in form.editable_fields:
                    field.disabled = True
                form.editable_fields = []
                
            if toggle_edit:
                  for field in form.editable_fields:
                        classes = field.widget.attrs.get("class","").split(" ")
                        field.widget.attrs["class"] = (" ".join(classes) + " toggle_edit").strip()
                        field.disabled = True
        else:
            new_class.edit = False
            new_class.toggle_edit = False

        return new_class


class ModelFormSet(BaseModelFormSet, metaclass=ModelFormSetMeta):

    DEFAULT_FILTER = 0
    AJAX_FILTER = 1
    ACTIVE_FILTER = 2

    filter_types = [
        DEFAULT_FILTER,
        AJAX_FILTER,
        ACTIVE_FILTER
    ]
    
    extra=0
    can_order=False
    can_delete=False
    max_num=DEFAULT_MAX_NUM
    validate_max=False
    min_num=DEFAULT_MIN_NUM
    validate_min=False
    absolute_max=None
    can_delete_extra=True

    view = True
    select = True
    delete = True
    json = False
    
    edit = True
    toggle_edit = False
    
    create = False
    
    paginate = True
    forms_per_page = 30
    
    filter = None
    filter_type = DEFAULT_FILTER

class InlineModelFormSetMeta(ModelFormSetMeta):
    def check_bases(self, bases):
        return bases == (ModelFormSet,)

class InlineModelFormSet(ModelFormSet,metaclass=InlineModelFormSetMeta):
    filter_type = ModelFormSet.ACTIVE_FILTER

    view = False
    edit = True
    
    """A formset for child objects related to a parent."""
    def __init__(self, data=None, files=None, instance=None,
                  prefix=None, queryset=None, **kwargs):
        if instance is None:
            raise Exception("Instance not provided at " + self.__class__.__name__)
        else:
            self.instance = instance
        if queryset is None:
            queryset = self.model._default_manager
        if self.instance.pk is not None:
            qs = queryset.filter(**{self.fk.name: self.instance})
        else:
            qs = queryset.none()
        super().__init__(data, files, prefix=prefix, queryset=qs, **kwargs)


