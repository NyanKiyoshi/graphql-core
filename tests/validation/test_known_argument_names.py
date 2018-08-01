from graphql.validation import KnownArgumentNamesRule
from graphql.validation.rules.known_argument_names import (
    unknown_arg_message, unknown_directive_arg_message)

from .harness import expect_fails_rule, expect_passes_rule


def unknown_arg(arg_name, field_name, type_name, suggested_args, line, column):
    return {
        'message': unknown_arg_message(
            arg_name, field_name, type_name, suggested_args),
        'locations': [(line, column)]}


def unknown_directive_arg(
        arg_name, directive_name, suggested_args, line, column):
    return {
        'message': unknown_directive_arg_message(
            arg_name, directive_name, suggested_args),
        'locations': [(line, column)]}


def describe_validate_known_argument_names():

    def single_arg_is_known():
        expect_passes_rule(KnownArgumentNamesRule, """
            fragment argOnRequiredArg on Dog {
              doesKnowCommand(dogCommand: SIT)
            }
            """)

    def multiple_args_are_known():
        expect_passes_rule(KnownArgumentNamesRule, """
            fragment multipleArgs on ComplicatedArgs {
              multipleReqs(req1: 1, req2: 2)
            }
            """)

    def ignore_args_of_unknown_fields():
        expect_passes_rule(KnownArgumentNamesRule, """
            fragment argOnUnknownField on Dog {
              unknownField(unknownArg: SIT)
            }
            """)

    def multiple_args_in_reverse_order_are_known():
        expect_passes_rule(KnownArgumentNamesRule, """
            fragment multipleArgsReverseOrder on ComplicatedArgs {
              multipleReqs(req2: 2, req1: 1)
            }
            """)

    def no_args_on_optional_arg():
        expect_passes_rule(KnownArgumentNamesRule, """
            fragment noArgOnOptionalArg on Dog {
              isHousetrained
            }
            """)

    def args_are_known_deeply():
        expect_passes_rule(KnownArgumentNamesRule, """
            {
              dog {
                doesKnowCommand(dogCommand: SIT)
              }
              human {
                pet {
                  ... on Dog {
                      doesKnowCommand(dogCommand: SIT)
                  }
                }
              }
            }
            """)

    def directive_args_are_known():
        expect_passes_rule(KnownArgumentNamesRule, """
            {
              dog @skip(if: true)
            }
            """)

    def undirective_args_are_invalid():
        expect_fails_rule(KnownArgumentNamesRule, """
            {
              dog @skip(unless: true)
            }
            """, [
            unknown_directive_arg('unless', 'skip', [], 3, 25)
        ])

    def misspelled_directive_args_are_reported():
        expect_fails_rule(KnownArgumentNamesRule, """
            {
              dog @skip(iff: true)
            }
            """, [
            unknown_directive_arg('iff', 'skip', ['if'], 3, 25)
        ])

    def invalid_arg_name():
        expect_fails_rule(KnownArgumentNamesRule, """
            fragment invalidArgName on Dog {
              doesKnowCommand(unknown: true)
            }
            """, [
            unknown_arg('unknown', 'doesKnowCommand', 'Dog', [], 3, 31)
        ])

    def misspelled_args_name_is_reported():
        expect_fails_rule(KnownArgumentNamesRule, """
            fragment invalidArgName on Dog {
              doesKnowCommand(dogcommand: true)
            }
            """, [unknown_arg(
                'dogcommand', 'doesKnowCommand', 'Dog', ['dogCommand'], 3, 31)
        ])

    def unknown_args_amongst_known_args():
        expect_fails_rule(KnownArgumentNamesRule, """
            fragment oneGoodArgOneInvalidArg on Dog {
              doesKnowCommand(whoknows: 1, dogCommand: SIT, unknown: true)
            }
            """, [
            unknown_arg('whoknows', 'doesKnowCommand', 'Dog', [], 3, 31),
            unknown_arg('unknown', 'doesKnowCommand', 'Dog', [], 3, 61)
        ])

    def unknown_args_deeply():
        expect_fails_rule(KnownArgumentNamesRule, """
            {
              dog {
                doesKnowCommand(unknown: true)
              }
              human {
                pet {
                  ... on Dog {
                    doesKnowCommand(unknown: true)
                  }
                }
              }
            }
            """, [
            unknown_arg('unknown', 'doesKnowCommand', 'Dog', [], 4, 33),
            unknown_arg('unknown', 'doesKnowCommand', 'Dog', [], 9, 37)
        ])
