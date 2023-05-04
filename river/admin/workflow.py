from django import forms
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType

from river.core.workflowregistry import workflow_registry
from river.models import Workflow


def get_workflow_choices():
    class_by_id = lambda cid: workflow_registry.class_index[cid]
    result = []
    for class_id, field_names in workflow_registry.workflows.items():
        cls = class_by_id(class_id)
        content_type = ContentType.objects.get_for_model(cls)
        result.extend(
            (
                f"{content_type.pk} {field_name}",
                f"{cls.__module__}.{cls.__name__} - {field_name}",
            )
            for field_name in field_names
        )
    return result


class WorkflowForm(forms.ModelForm):
    workflow = forms.ChoiceField(choices=[])

    class Meta:
        model = Workflow
        fields = ('workflow', 'initial_state')

    def __init__(self, *args, **kwargs):
        instance = kwargs.get("instance", None)
        self.declared_fields['workflow'].choices = get_workflow_choices()
        if instance and instance.pk:
            self.declared_fields[
                'workflow'
            ].initial = f"{instance.content_type.pk} {instance.field_name}"

        super(WorkflowForm, self).__init__(*args, **kwargs)

    def clean_workflow(self):
        if self.cleaned_data.get('workflow') == '' or ' ' not in self.cleaned_data.get('workflow'):
            return None, None
        else:
            return self.cleaned_data.get('workflow').split(" ")

    def save(self, *args, **kwargs):
        content_type_pk, field_name = self.cleaned_data.get('workflow')
        instance = super(WorkflowForm, self).save(commit=False)
        instance.content_type = ContentType.objects.get(pk=content_type_pk)
        instance.field_name = field_name
        return super(WorkflowForm, self).save(*args, **kwargs)


# noinspection PyMethodMayBeStatic
class WorkflowAdmin(admin.ModelAdmin):
    form = WorkflowForm
    list_display = ('model_class', 'field_name', 'initial_state')

    def model_class(self, obj):
        if cls := obj.content_type.model_class():
            return f"{cls.__module__}.{cls.__name__}"
        else:
            return "Class not found in the workspace"

    def field_name(self, obj):  # pylint: disable=no-self-use
        return obj.workflow.field_name


admin.site.register(Workflow, WorkflowAdmin)
