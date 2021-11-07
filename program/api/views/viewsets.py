from django.db.models.fields.related import ManyToManyField, OneToOneField
from django.forms.models import modelform_factory
from django.http.response import JsonResponse
from django.urls import path, include
from request_funkcije import *
import sys
from django.shortcuts import get_object_or_404, redirect
from django.core.paginator import EmptyPage, PageNotAnInteger
from django.core.paginator import Paginator as DefaultPaginator
import re
from program.api.forms.formsets import BaseFormSet
from program.api.forms.forms import ModelForm, RowModelForm
from django.views import View
from django.contrib.auth.decorators import login_required
from django.db.models.fields.reverse_related import ManyToOneRel

class Paginator(DefaultPaginator):
    def __init__(self, object_list, per_page, orphans=0,
                allow_empty_first_page=True, current_page=0, on_each_side=2, on_ends=2):
        self.on_each_side = on_each_side
        self.on_ends = on_ends
        self.object_list = object_list
        self._check_object_list_is_ordered()
        self.per_page = int(per_page)
        self.orphans = int(orphans)
        self.allow_empty_first_page = allow_empty_first_page
        self.current_page = self.page(current_page)

    @property
    def pages(self):
        elided_pages = list(self.get_elided_page_range(self.current_page.number,
            on_each_side=self.on_each_side,
            on_ends = self.on_ends))
        index = 0
        pages = []
        for page_number in elided_pages:
            if page_number == self.ELLIPSIS:
                page = self.page((elided_pages[index - 1] + elided_pages[index + 1]) // 2 )
                page.display = self.ELLIPSIS
            else:
                page = self.page(page_number)
                page.display = page_number
            index += 1
            pages.append(page)
        return pages

class ViewSet():
    def __init__(self):
        self._prefix = None

    def urls(self):
        return []

    def _get_prefix(self):
        if self._prefix:
            return self._prefix
        else:
            return re.sub('(?!^)([A-Z]+)', r'_\1',self.__class__.__name__).lower()

    def _set_prefix(self,prefix):
        self._prefix = prefix

    prefix = property(_get_prefix, _set_prefix)

##############################################################################################
¸¸¸¸
def components_for_model(model,exclude,components):
    form = components.get("model")
    komponente = {}
    if not form:
        form = modelform_factory(model)
    komponente["model"] = model
    for one_to_one in [field for field in model._meta.get_fields() if field.__class__ == OneToOneField]:
        field_name = one_to_one.name
        form = components.get(field_name)
        if not form:
            related_model = one_to_one.related_model
            form = modelform_factory(related_model)
        komponente[field_name] = model
    for foreign_key in [field for field in model._meta.get_fields() if field.__class__ == ManyToOneRel]:
        field_name = foreign_key.get_accessor_name()
        formset = components.get(field_name)
        if not formset:
            related_model = foreign_key.related_model
            #formset = inline_model_formset_factory(model,related_model)
        komponente[field_name] = formset
    for many_to_many in [field for field in model._meta.get_fields() if field.__class__ == ManyToManyField]:
        field_name = many_to_many.get_accessor_name()
        formset = components.get(field_name)
        if not formset:
            related_model = many_to_many.related_model
            #formset = many_to_many_model_formset_factory(model,related_model)
        komponente[field_name] = formset
    komponente.update(components)
    return komponente

class ModelViewSetOptions():
    model = None
    forms = None
    many_to_many = None

class ModeltViewSetMeta():
    pass

class ModelViewSet(ViewSet):
    model = None
    exclude = None
    after_delete = None

    components = {

    }
    
    layout = None


    def model_view(self,request, pk, **kwargs):
        instance = get_object_or_404(self.model,pk=pk)
        slovar = {
            "instance": instance
        }
        return pokazi_stran(request, self.model_template_path, slovar)

    def edit_form_ajax(self,request,pk,**kwargs):
        instance = get_object_or_404(self.model,pk=pk)
        form = self.forms.get(request.POST.get("form"))(data=request.POST, instance=instance)
        form.save()
        data = {
            "values": form.values(),
            "connected":{
            connected_form.prefix: connected_form(instance=instance).values
            for connected_form in form.connected_forms}
        }
        return JsonResponse(data, safe=False)
        
    #ACTION
    def delete(self,request,pk,**kwargs):
        instance = get_object_or_404(self.model,pk=pk)
        instance.delete()
        if self.after_delete:
            return redirect(self.after_delete,**kwargs)
        else:
            return redirect("home")

    #ACTION
    def pdf(self,request,pk,**kwargs):
        instance = get_object_or_404(self.model,pk=pk)
        return instance.construct_pdf()

    #ACTION
    def json(self,request,pk,**kwargs):
        instance = get_object_or_404(self.model, pk=pk)
        return JsonResponse(instance.all_values())

    @login_required
    def save_form(self,request,pk,**kwargs):
        prefix = request.POST.get("form")
        form = self.components.get(prefix)
        if form:
            form.save(request.POST)
        if request.is_ajax():
            data = {
                "form": form.data,
                "connected": {
                    connected.refresh_data() for connected in form.connected_components
                }
            }
            return JsonResponse(data,safe=False)
        else:
            return redirect("/")

    def save_inline_formset(self,request,pk, **kwargs):
        pass

    def delete_inline_formset(self,request,pk,**kwargs):
        pass

    def save_row_inline_formset(self,request,pk,**kwargs):
        prefix = request.POST.get("formset")
        formset = self.components.get(prefix)
        form = request.POST.get("form")
        if formset:
            form = formset.form(id=form)
            form.save(request.POST)
        if request.is_ajax():
            data = {
                "form": form.data,
                "connected": {
                    connected.refresh_data() for connected in formset.connected_components
                }
            }
            return JsonResponse(data,safe=False)
        else:
            return redirect("/")

    def delete_row_inline_formset(self,request,pk,**kwargs):
        prefix = request.POST.get("formset")
        formset = self.components.get(prefix)
        if formset:
            pk = request.POST.get("pk")
            instance = get_object_or_404(formset.model,pk=pk)
            instance.delete()
        if request.is_ajax():
            data = {
                "connected": {
                    connected.refresh_data() for connected in formset.connected_components
                }
            }
            return JsonResponse(data,safe=False)
        else:
            return redirect("/")

    def add_row_inline_formset(self,request,pk,**kwargs):
        pass

    def add_rows_from_file_inline_formset(self,request,pk,**kwargs):
        pass

    def add_many_to_many(self,request,pk,**kwargs):
        pass

    def remove_many_to_many(self,request,pk,**kwargs):
        pass


class ModelListViewSetOptions():
    model = None
    formset = None
    model_view_set = None

class ModelListViewSetMeta(type):
    def __new__(mcs, name, bases, attrs):
        new_class = super().__new__(mcs, name, bases, attrs)
                
        if bases == (ViewSet,):
            return new_class
        formset = attrs.get('formset')

        if not formset or not issubclass(formset,BaseFormSet) or formset == BaseFormSet:
            raise Exception("Formset not provided or is incorrect at %s" % name)
        
        model = attrs.get("model")
        if not model:
            raise Exception("Model not provided at %s" % name)

        model_view_set = attrs.get("model_view_set")
        if not model_view_set or not issubclass(model_view_set, ModelViewSet) or model_view_set == ModelViewSet:
            new_class.formset.view = False

        # DODAJ MOŽNOST ROW CREATE IN RAZDELAJ MOŽNOSTI
        create = attrs.get("create")
        if not isinstance(create,type):
            pass
        elif issubclass(create,View):
            new_class.create_type = "view"
        elif issubclass(create, RowModelForm):
            new_class.formset.create_form = create
            new_class.create_type = "row"
        elif issubclass(create, ModelForm):
            new_class.create_type = "form"
        
        return new_class

class ModelListViewSet(ViewSet, metaclass=ModelListViewSetMeta):
    template_path = "views/list_view.html"
    
    model = None
    formset = None
    model_view_set = None
    
    always_display_create = False
    create_type = None
    create = None

    def __init__(self):
        ViewSet.__init__(self)
        if self.model_view_set:
            self.model_view_set.after_delete = self.prefix + "_list_view"
            
    def urls(self):
        name_prefix = self.prefix
        prefix = self.model.__name__.lower()
        paths = [
            path(prefix + "/",self.list_view, name= name_prefix + "_list_view"),
            path(prefix + "/list_update_ajax/",self.list_update_ajax, name= prefix + "_list_update_ajax"),
            path(prefix + "/list_update/",self.list_update, name= prefix + "_list_update"),
            path(prefix + "/list_delete_ajax/",self.list_delete_ajax, name= prefix + "_list_delete_ajax"),
            path(prefix + "/list_delete/",self.list_delete, name= prefix + "_list_delete"),
            path(prefix + "/delete_ajax/<int:pk>/", self.model_delete_ajax, name = prefix + "_model_delete_ajax"),
            path(prefix + "/delete/<int:pk>/", self.model_delete, name = prefix + "_model_delete"),
            path(prefix + "/create_ajax/", self.model_create_ajax, name = prefix + "_model_create_ajax"),
            path(prefix + "/create/", self.model_create, name = prefix + "_model_create"),
            path(prefix + "/update_ajax/<int:pk>/", self.model_update_ajax, name = prefix + "_model_update_ajax"),
            path(prefix + "/update/<int:pk>/", self.model_update, name = prefix + "_model_update"),
        ]
        if self.model_view_set:
            paths.append(path(prefix + "/ogled/<int:pk>/", include(self.model_view_set.urls())))
        return paths

    def _get_queryset(self,request=None):
        return self._queryset

    def _set_queryset(self,queryset):
        self._queryset = queryset    

    queryset = property(_get_queryset,_set_queryset)

    def model_create_ajax(self,request,**kwargs):
        pass

    def model_create(self,request, **kwargs):
        pass

    def model_update_ajax(self,request,pk,**kwargs):
        object = get_object_or_404(self.model, pk=pk)
        form = self.formset.form(instance = object)
        form.save(request.POST)
        data = {
            "success" : True,
            "model": object.all_values()
        }
        return JsonResponse(data, safe=False)

    def model_update(self,request,pk, **kwargs):
        object = get_object_or_404(self.model, pk=pk)
        form = self.model_form(instance = object)
        form.save()
        return redirect(self.get_prefix() + "_list_view", **kwargs)

    def model_delete_ajax(self,request,pk, **kwargs):
        object = get_object_or_404(self.model, pk=pk)
        print(object)
        object.delete()
        print("DELAM")
        data = {"success":True}
        return JsonResponse(data, safe=False)

    def model_delete(self,request,pk, **kwargs):
        object = get_object_or_404(self.model, pk=pk)
        object.delete()
        return redirect("/",**kwargs)

    def list_view(self,request, **kwargs):
        formset = self.formset
        filter = formset.filter
        queryset = self.model.objects.all()
        if filter != None:
            filter = filter(request.GET, queryset=queryset)
            queryset = filter.qs
        if formset.paginate:
            page = request.GET.get("page",1)
            paginator = Paginator(queryset, formset.forms_per_page,current_page=page)
            page_query = paginator.page(page)
            queryset = self.queryset =  queryset.filter(id__in = [object.id for object in page_query])
        slovar = {
            "title": self.model.plural if self.list_view_title == None else self.list_view_title,
            "filter": filter,
            "formset": self.formset(queryset=queryset),
            "paginator":paginator,
            "create": self.create,
            "create_type": self.create_type,
            "always_display_create":self.always_display_create
        }
        return pokazi_stran(request, self.template_path, slovar)

    def list_update_ajax(self,request, **kwargs):
        pass

    def list_update(self, reqeust,**kwargs):
        pass

    def list_delete_ajax(self, request,**kwargs):
        pass

    def list_delete(self,request, **kwargs):
        print(request.POST.get("next"))
        print(self.queryset.all_values())
        return redirect(request.POST.get("next"), **kwargs)

