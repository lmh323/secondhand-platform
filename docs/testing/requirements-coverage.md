# Requirements Coverage Report

Status: Stage 5 verification result

The table maps each mandatory user story to executable tests. The latest run used Python 3.12.7 on 2026-10-28 and completed 31 tests with 0 failures and 0 errors.

| User story | Verification tests | Result |
| --- | --- | --- |
| US1 | `tests.model.test_pir.PIRConstructionTests.test_all_record_types_store_required_fields`; `tests.cli.test_cli.ControllerTests.test_controller_supports_create_update_search_print_and_delete` | PASS |
| US2 | `tests.model.test_pir.PIRConstructionTests.test_all_record_types_store_required_fields`; `tests.model.test_pir.PIRConstructionTests.test_required_values_and_identifiers_are_validated`; `tests.test_main.MainLoopTests.test_run_processes_commands_and_continues_after_syntax_errors` | PASS |
| US3 | `tests.model.test_pir.PIRConstructionTests.test_all_record_types_store_required_fields`; `tests.model.test_pir.PIRConstructionTests.test_required_values_and_identifiers_are_validated`; `tests.model.test_pir.PIRUpdateTests.test_updates_change_fields_without_changing_identity_or_type` | PASS |
| US4 | `tests.model.test_pir.PIRConstructionTests.test_all_record_types_store_required_fields`; `tests.model.test_pir.PIRConstructionTests.test_required_values_and_identifiers_are_validated`; `tests.model.test_search.SearchTests.test_time_search_skips_records_without_the_requested_field` | PASS |
| US5 | `tests.model.test_pir.PIRConstructionTests.test_all_record_types_store_required_fields`; `tests.model.test_pir.PIRConstructionTests.test_required_values_and_identifiers_are_validated`; `tests.model.test_pir.PIRUpdateTests.test_updates_change_fields_without_changing_identity_or_type` | PASS |
| US6 | `tests.model.test_pir.PIRUpdateTests.test_updates_change_fields_without_changing_identity_or_type`; `tests.model.test_pir.PIRUpdateTests.test_invalid_multi_field_update_is_atomic`; `tests.cli.test_cli.ControllerTests.test_controller_reports_errors_without_corrupting_repository` | PASS |
| US7 | `tests.model.test_search.SearchTests.test_type_and_case_insensitive_text_search`; `tests.model.test_search.SearchTests.test_time_search_skips_records_without_the_requested_field`; `tests.model.test_search.SearchTests.test_boolean_precedence_and_parentheses`; `tests.model.test_search.SearchTests.test_invalid_criteria_are_rejected` | PASS |
| US8 | `tests.model.test_repository.RepositoryTests.test_replace_sorts_records_and_resets_next_identifier`; `tests.cli.test_cli.ControllerTests.test_controller_supports_create_update_search_print_and_delete`; `tests.cli.test_cli.ViewTests.test_view_renders_each_result_kind` | PASS |
| US9 | `tests.model.test_repository.RepositoryTests.test_get_update_delete_and_missing_ids`; `tests.cli.test_cli.ControllerTests.test_controller_supports_create_update_search_print_and_delete` | PASS |
| US10 | `tests.model.test_persistence.PersistenceTests.test_round_trip_preserves_all_record_types_and_ids`; `tests.model.test_persistence.PersistenceTests.test_save_validates_path_and_record_values`; `tests.cli.test_cli.ControllerTests.test_controller_save_load_and_failed_load_are_safe` | PASS |
| US11 | `tests.model.test_persistence.PersistenceTests.test_load_rejects_missing_malformed_incompatible_and_duplicate_files`; `tests.cli.test_cli.ControllerTests.test_controller_save_load_and_failed_load_are_safe` | PASS |

## Additional non-functional verification

- **NFR-01 / NFR-02:** tests import the model and CLI packages directly using the Python standard library; no network or third-party runtime dependency is used.
- **NFR-03 / NFR-05:** parser, controller, view, and main-loop tests verify human-readable error results and continued command processing.
- **NFR-04:** persistence round-trip tests compare every serialized record and identifier.
- **NFR-06:** repository tests verify stable ID ordering for print and search results.
- **NFR-08:** successful and validation-failure paths are covered for public model operations.
- **NFR-09:** tests use workspace-local files and do not contact a network service.
