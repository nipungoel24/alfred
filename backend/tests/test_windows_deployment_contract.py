"""Windows release/deployment contract regression tests."""

from tools.release import check_windows_deployment as contract


def test_no_custom_nsis_shortcut_repair_hook():
    contract.test_no_custom_nsis_shortcut_repair_hook()


def test_no_prebuilt_shortcuts_are_bundled():
    contract.test_no_prebuilt_shortcuts_are_bundled()


def test_no_runtime_sensitive_user_paths_in_release_sources():
    contract.test_no_runtime_sensitive_user_paths_in_release_sources()


def test_tauri_uses_standard_per_user_nsis_and_external_sidecar():
    contract.test_tauri_uses_standard_per_user_nsis_and_external_sidecar()


def test_frontend_packaged_tauri_does_not_fall_back_to_dev_port():
    contract.test_frontend_packaged_tauri_does_not_fall_back_to_dev_port()


def test_sidecar_resolution_uses_tauri_external_bin_not_cwd():
    contract.test_sidecar_resolution_uses_tauri_external_bin_not_cwd()


def test_build_identity_is_logged():
    contract.test_build_identity_is_logged()


# ── Credential containment ─────────────────────────────────────────


def test_sidecar_builder_never_stages_a_client_secret():
    contract.test_sidecar_builder_never_stages_a_client_secret()


def test_sidecar_builder_refuses_to_build_with_a_client_secret():
    contract.test_sidecar_builder_refuses_to_build_with_a_client_secret()


def test_frozen_build_rejects_a_client_secret():
    contract.test_frozen_build_rejects_a_client_secret()


def test_release_secret_scanner_exists_and_covers_known_patterns():
    contract.test_release_secret_scanner_exists_and_covers_known_patterns()


def test_staged_release_config_on_disk_has_no_secret():
    contract.test_staged_release_config_on_disk_has_no_secret()


# ── Startup lifecycle ──────────────────────────────────────────────


def test_main_window_is_created_visible():
    contract.test_main_window_is_created_visible()


def test_reveal_is_not_confined_to_the_single_instance_callback():
    contract.test_reveal_is_not_confined_to_the_single_instance_callback()


def test_production_csp_has_no_development_origin():
    contract.test_production_csp_has_no_development_origin()


def test_session_token_comes_from_the_os_csprng():
    contract.test_session_token_comes_from_the_os_csprng()


def test_readiness_is_protocol_based_not_a_substring_match():
    contract.test_readiness_is_protocol_based_not_a_substring_match()


def test_exit_does_not_depend_on_winning_a_lock_race():
    contract.test_exit_does_not_depend_on_winning_a_lock_race()


def test_session_token_is_never_logged():
    contract.test_session_token_is_never_logged()


def test_credential_store_is_fail_closed():
    contract.test_credential_store_is_fail_closed()
