import inspect

from django import forms
from django.core import serializers

from export import fields


class Export(forms.Form):
    export_format = forms.ChoiceField(
        choices=[(format, format) for format in \
                serializers.get_serializer_formats()],
        required=False,
        label='Format',
        help_text='Designates export format.',
    )
    export_fields = forms.MultipleChoiceField(
        choices=[],
        required=False,
        label='Fields',
        help_text="Fields to be included in the exported data. If none are \
                selected all fields will be exported. Hold down 'Control', \
                or 'Command' on a Mac, to select more than one.",
    )
    export_order_by = forms.ChoiceField(
        required=False,
        label='Order by',
        help_text='Field to use for export ordering.',
    )
    export_order_direction = forms.ChoiceField(
        choices=[('asc', 'Ascending'), ('dsc', 'Descending')],
        required=False,
        label='Order direction',
        help_text='Sort elements in ascending or descending order.',
    )

    def __init__(self, model, *args, **kwargs):
        super(Export, self).__init__(*args, **kwargs)
        self.fieldsets = (('Options', {'fields': ('export_format', \
                'export_fields', 'export_order_by', \
                'export_order_direction')}), ('Filters', \
                {'description': 'Objects will be filtered to match the \
                criteria as specified in the fields below. If a value \
                is not specified for a field the field is ignored during \
                the filter process.', 'fields': []}))

        field_choices = []
        form_fields = forms.models.fields_for_model(model)
        for field in model._meta.fields:
            name = field.name
            if name in form_fields.keys():
                form_field = form_fields[name]
            else:
                form_field = field.formfield()
            if not form_field:
                continue
            if form_field.__class__ in [forms.models.ModelChoiceField, \
                    forms.models.ModelMultipleChoiceField]:
                self.fields[name] = getattr(fields, field.__class__.\
                        __name__)(form_field, form_field.queryset)
            else:
                try:
                    self.fields[name] = getattr(fields, \
                            field.__class__.__name__)(form_field)
                except AttributeError:
                    for parent_field in inspect.getmro(field.__class__):
                        if parent_field.__module__ == \
                                'django.db.models.fields':
                            self.fields[name] = getattr(\
                                    fields, parent_field.__name__)(form_field)
                            break

            if name not in self.fieldsets[1][1]['fields']:
                self.fieldsets[1][1]['fields'].append(name)

            field_choices.append([name, form_field.label.capitalize()])

        self.fields['export_fields'].choices = field_choices
        self.fields['export_order_by'].choices = field_choices
