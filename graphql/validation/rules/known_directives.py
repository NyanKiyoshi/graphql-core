from typing import cast

from ...error import GraphQLError
from ...language import DirectiveLocation, Node, OperationDefinitionNode
from . import ValidationRule

__all__ = [
    'KnownDirectivesRule',
    'unknown_directive_message', 'misplaced_directive_message']


def unknown_directive_message(directive_name: str) -> str:
    return f"Unknown directive '{directive_name}'."


def misplaced_directive_message(directive_name, location):
    return f"Directive '{directive_name}' may not be used on {location}."


class KnownDirectivesRule(ValidationRule):
    """Known directives

    A GraphQL document is only valid if all `@directives` are known by the
    schema and legally positioned.
    """

    def enter_directive(self, node, _key, _parent, _path, ancestors):
        for definition in self.context.schema.directives:
            if definition.name == node.name.value:
                candidate_location = get_directive_location_for_ast_path(
                    ancestors)
                if (candidate_location
                        and candidate_location not in definition.locations):
                    self.report_error(GraphQLError(
                        misplaced_directive_message(
                            node.name.value, candidate_location.value),
                        [node]))
                break
        else:
            self.report_error(GraphQLError(
                unknown_directive_message(node.name.value), [node]))


_operation_location = {
    'query': DirectiveLocation.QUERY,
    'mutation': DirectiveLocation.MUTATION,
    'subscription': DirectiveLocation.SUBSCRIPTION}

_directive_location = {
    'field': DirectiveLocation.FIELD,
    'fragment_spread': DirectiveLocation.FRAGMENT_SPREAD,
    'inline_fragment': DirectiveLocation.INLINE_FRAGMENT,
    'fragment_definition': DirectiveLocation.FRAGMENT_DEFINITION,
    'schema_definition': DirectiveLocation.SCHEMA,
    'schema_extension': DirectiveLocation.SCHEMA,
    'scalar_type_definition': DirectiveLocation.SCALAR,
    'scalar_type_extension': DirectiveLocation.SCALAR,
    'object_type_definition': DirectiveLocation.OBJECT,
    'object_type_extension': DirectiveLocation.OBJECT,
    'field_definition': DirectiveLocation.FIELD_DEFINITION,
    'interface_type_definition': DirectiveLocation.INTERFACE,
    'interface_type_extension': DirectiveLocation.INTERFACE,
    'union_type_definition': DirectiveLocation.UNION,
    'union_type_extension': DirectiveLocation.UNION,
    'enum_type_definition': DirectiveLocation.ENUM,
    'enum_type_extension': DirectiveLocation.ENUM,
    'enum_value_definition': DirectiveLocation.ENUM_VALUE,
    'input_object_type_definition': DirectiveLocation.INPUT_OBJECT,
    'input_object_type_extension': DirectiveLocation.INPUT_OBJECT}


def get_directive_location_for_ast_path(ancestors):
    applied_to = ancestors[-1]
    if isinstance(applied_to, Node):
        kind = applied_to.kind
        if kind == 'operation_definition':
            applied_to = cast(OperationDefinitionNode, applied_to)
            return _operation_location.get(applied_to.operation.value)
        elif kind == 'input_value_definition':
            parent_node = ancestors[-3]
            return (DirectiveLocation.INPUT_FIELD_DEFINITION
                    if parent_node.kind == 'input_object_type_definition'
                    else DirectiveLocation.ARGUMENT_DEFINITION)
        else:
            return _directive_location.get(kind)
