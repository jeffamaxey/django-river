import inspect

from river.core.classworkflowobject import ClassWorkflowObject
from river.core.instanceworkflowobject import InstanceWorkflowObject
from river.core.workflowregistry import workflow_registry


# noinspection PyMethodMayBeStatic
class RiverObject(object):

    def __init__(self, owner):
        self.owner = owner
        self.is_class = inspect.isclass(owner)

    def __getattr__(self, field_name):
        cls = self.owner if self.is_class else self.owner.__class__
        if field_name not in workflow_registry.workflows[id(cls)]:
            raise Exception(
                f"Workflow with name:{field_name} doesn't exist for class:{cls.__name__}"
            )
        if self.is_class:
            return ClassWorkflowObject(self.owner, field_name)
        else:
            return InstanceWorkflowObject(self.owner, field_name)

    def all(self, cls):
        return [
            getattr(self, field_name)
            for field_name in workflow_registry.workflows[id(cls)]
        ]

    def all_field_names(self, cls):  # pylint: disable=no-self-use
        return list(workflow_registry.workflows[id(cls)])
