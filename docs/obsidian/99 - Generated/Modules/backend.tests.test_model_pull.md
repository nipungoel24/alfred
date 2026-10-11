---
type: module
generated: true
language: python
layer: backend
qualified_name: backend.tests.test_model_pull
source: backend/tests/test_model_pull.py
status: active
tags: [module, backend]
---

# backend.tests.test_model_pull

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Source

`backend/tests/test_model_pull.py`

## Imports

- `DiskStatus` ← `backend.app.ai.resources.DiskStatus`
- `LayerProgressAggregator` ← `backend.app.ai.ollama_client.LayerProgressAggregator`
- `MIN_DOWNLOAD_RAM_BYTES` ← `backend.app.ai.resources.MIN_DOWNLOAD_RAM_BYTES`
- `NdjsonStreamDecoder` ← `backend.app.ai.ollama_client.NdjsonStreamDecoder`
- `OllamaClient` ← `backend.app.ai.ollama_client.OllamaClient`
- `OllamaInsufficientSpace` ← `backend.app.ai.ollama_client.OllamaInsufficientSpace`
- `OllamaPullFailed` ← `backend.app.ai.ollama_client.OllamaPullFailed`
- `PullProgress` ← `backend.app.ai.ollama_client.PullProgress`
- `asyncio` ← `asyncio`
- `check_for_model_download` ← `backend.app.ai.resources.check_for_model_download`
- `disk_status` ← `backend.app.ai.resources.disk_status`
- `httpx` ← `httpx`
- `human_bytes` ← `backend.app.ai.resources.human_bytes`
- `installed_ram_bytes` ← `backend.app.ai.resources.installed_ram_bytes`
- `iter_ndjson_records` ← `backend.app.ai.ollama_client.iter_ndjson_records`
- `ollama_models_dir` ← `backend.app.ai.resources.ollama_models_dir`
- `pytest` ← `pytest`

## Classes

- [[backend.tests.test_model_pull._ChunkStream|_ChunkStream]]
- [[backend.tests.test_model_pull._StreamTransport|_StreamTransport]]

## Functions

- [[backend.tests.test_model_pull._ChunkStream.__aiter__|__aiter__]]
- [[backend.tests.test_model_pull._ChunkStream.__init__|__init__]]
- [[backend.tests.test_model_pull._ChunkStream.aclose|aclose]]
- [[backend.tests.test_model_pull._StreamTransport.__init__|__init__]]
- [[backend.tests.test_model_pull._StreamTransport.handle_async_request|handle_async_request]]
- [[backend.tests.test_model_pull._client_for|_client_for]]
- [[backend.tests.test_model_pull._lines|_lines]]
- [[backend.tests.test_model_pull.test_cancelling_the_pull_task_closes_the_stream.run|run]]
- [[backend.tests.test_model_pull.test_list_models_reports_names_and_sizes_without_invention.tags|tags]]
- [[backend.tests.test_model_pull.test_model_size_uses_the_real_reported_size.tags|tags]]
- [[backend.tests.test_model_pull.test_pull_error_record_raises_and_is_not_reported_as_success.run|run]]
- [[backend.tests.test_model_pull.test_pull_http_error_status_raises.run|run]]
- [[backend.tests.test_model_pull.test_pull_non_success_terminal_status_raises.run|run]]
- [[backend.tests.test_model_pull.test_pull_reports_real_progress_and_completes.run|run]]
- [[backend.tests.test_model_pull.test_pull_splits_records_across_chunks_while_streaming.run|run]]
- [[backend.tests.test_model_pull.test_space_check_aborts_the_download_before_it_fills_the_disk.check|check]]
- [[backend.tests.test_model_pull.test_space_check_aborts_the_download_before_it_fills_the_disk.run|run]]
- [[backend.tests.test_model_pull.test_space_check_runs_once_with_the_announced_total_before_progress.check|check]]
- [[backend.tests.test_model_pull.test_space_check_runs_once_with_the_announced_total_before_progress.run|run]]

## Tests

- [[backend.tests.test_model_pull.test_blank_lines_are_ignored|test_blank_lines_are_ignored]]
- [[backend.tests.test_model_pull.test_cancelling_the_pull_task_closes_the_stream|test_cancelling_the_pull_task_closes_the_stream]]
- [[backend.tests.test_model_pull.test_disk_status_reports_real_free_space|test_disk_status_reports_real_free_space]]
- [[backend.tests.test_model_pull.test_disk_status_walks_up_to_an_existing_ancestor|test_disk_status_walks_up_to_an_existing_ancestor]]
- [[backend.tests.test_model_pull.test_fraction_is_capped_at_one|test_fraction_is_capped_at_one]]
- [[backend.tests.test_model_pull.test_fraction_is_none_until_a_total_is_announced|test_fraction_is_none_until_a_total_is_announced]]
- [[backend.tests.test_model_pull.test_fraction_reflects_real_bytes|test_fraction_reflects_real_bytes]]
- [[backend.tests.test_model_pull.test_human_bytes_formats_consistently|test_human_bytes_formats_consistently]]
- [[backend.tests.test_model_pull.test_incomplete_final_record_is_not_emitted_until_flush|test_incomplete_final_record_is_not_emitted_until_flush]]
- [[backend.tests.test_model_pull.test_incomplete_final_record_without_newline_is_emitted_by_flush|test_incomplete_final_record_without_newline_is_emitted_by_flush]]
- [[backend.tests.test_model_pull.test_installed_ram_is_reported_as_a_real_value|test_installed_ram_is_reported_as_a_real_value]]
- [[backend.tests.test_model_pull.test_insufficient_disk_space_blocks_with_an_actionable_message|test_insufficient_disk_space_blocks_with_an_actionable_message]]
- [[backend.tests.test_model_pull.test_list_models_reports_names_and_sizes_without_invention|test_list_models_reports_names_and_sizes_without_invention]]
- [[backend.tests.test_model_pull.test_low_ram_blocks_before_a_download_starts|test_low_ram_blocks_before_a_download_starts]]
- [[backend.tests.test_model_pull.test_malformed_record_is_dropped_without_losing_neighbours|test_malformed_record_is_dropped_without_losing_neighbours]]
- [[backend.tests.test_model_pull.test_model_size_uses_the_real_reported_size|test_model_size_uses_the_real_reported_size]]
- [[backend.tests.test_model_pull.test_models_dir_is_a_real_path_on_this_machine|test_models_dir_is_a_real_path_on_this_machine]]
- [[backend.tests.test_model_pull.test_multi_byte_utf8_split_across_chunks|test_multi_byte_utf8_split_across_chunks]]
- [[backend.tests.test_model_pull.test_multiple_layers_are_summed_once_each|test_multiple_layers_are_summed_once_each]]
- [[backend.tests.test_model_pull.test_non_object_record_is_dropped|test_non_object_record_is_dropped]]
- [[backend.tests.test_model_pull.test_pull_error_record_raises_and_is_not_reported_as_success|test_pull_error_record_raises_and_is_not_reported_as_success]]
- [[backend.tests.test_model_pull.test_pull_http_error_status_raises|test_pull_http_error_status_raises]]
- [[backend.tests.test_model_pull.test_pull_non_success_terminal_status_raises|test_pull_non_success_terminal_status_raises]]
- [[backend.tests.test_model_pull.test_pull_reports_real_progress_and_completes|test_pull_reports_real_progress_and_completes]]
- [[backend.tests.test_model_pull.test_pull_splits_records_across_chunks_while_streaming|test_pull_splits_records_across_chunks_while_streaming]]
- [[backend.tests.test_model_pull.test_records_split_across_network_chunks_are_reassembled|test_records_split_across_network_chunks_are_reassembled]]
- [[backend.tests.test_model_pull.test_repeated_updates_for_one_digest_do_not_double_count|test_repeated_updates_for_one_digest_do_not_double_count]]
- [[backend.tests.test_model_pull.test_space_check_aborts_the_download_before_it_fills_the_disk|test_space_check_aborts_the_download_before_it_fills_the_disk]]
- [[backend.tests.test_model_pull.test_space_check_runs_once_with_the_announced_total_before_progress|test_space_check_runs_once_with_the_announced_total_before_progress]]
- [[backend.tests.test_model_pull.test_status_is_retained_across_layer_records|test_status_is_retained_across_layer_records]]
- [[backend.tests.test_model_pull.test_status_records_without_bytes_do_not_invent_a_total|test_status_records_without_bytes_do_not_invent_a_total]]
- [[backend.tests.test_model_pull.test_sufficient_space_and_ram_do_not_block|test_sufficient_space_and_ram_do_not_block]]
- [[backend.tests.test_model_pull.test_the_preflight_runs_against_this_machine|test_the_preflight_runs_against_this_machine]]
- [[backend.tests.test_model_pull.test_unknown_required_size_does_not_block|test_unknown_required_size_does_not_block]]
- [[backend.tests.test_model_pull.test_unparseable_incomplete_tail_is_dropped_not_invented|test_unparseable_incomplete_tail_is_dropped_not_invented]]
- [[backend.tests.test_model_pull.test_unreadable_disk_is_blocking|test_unreadable_disk_is_blocking]]
- [[backend.tests.test_model_pull.test_unreadable_ram_is_reported_as_uncertain_not_as_failure|test_unreadable_ram_is_reported_as_uncertain_not_as_failure]]
