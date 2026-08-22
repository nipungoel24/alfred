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
