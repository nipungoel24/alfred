"""Real local-system resource checks for the first-run AI setup path.

Everything here reads the actual machine. Nothing is estimated from a
constant, a hardcoded model size, or a demo hardware profile.

Only the standard library is used: `shutil.disk_usage` for the filesystem,
`ctypes`/`os.sysconf` for installed RAM. Adding a dependency for this would
be a worse answer than the platform APIs already provide (Rules §1.6).
"""

import ctypes
import logging
import os
import shutil
import sys
from dataclasses import dataclass

logger = logging.getLogger("alfred.ai.resources")


def ollama_models_dir() -> str:
    """The directory Ollama stores model layers in, on this machine.

    Precedence follows Ollama's own: `OLLAMA_MODELS`, then the per-OS
    default. The directory may not exist yet on a clean machine; that is a
    normal state and not an error.
    """
    override = os.environ.get("OLLAMA_MODELS", "").strip()
    if override:
        return override
    user_models = os.path.join(os.path.expanduser("~"), ".ollama", "models")
    if os.path.exists(user_models):
        return user_models
    if sys.platform == "win32":
        base = os.environ.get("LOCALAPPDATA", "") or os.path.expanduser("~")
        return os.path.join(base, "Ollama", "models")
    return user_models


@dataclass(frozen=True)
class DiskStatus:
    """Filesystem state at the Ollama model store.

    `total_bytes`/`free_bytes` are 0 and `error` is set when the platform
    call failed; a caller must never treat that as "no space needed".
    """

    path: str
    total_bytes: int
    free_bytes: int
    error: str | None = None

    @property
    def available(self) -> bool:
        return self.error is None


def disk_status(path: str | None = None) -> DiskStatus:
    """Read real free/total bytes for the filesystem holding `path`.

    `shutil.disk_usage` walks up to the mount point, so a not-yet-created
    models directory still reports the drive that will hold it — which is
    what a preflight check needs to answer.
    """
    target = path or ollama_models_dir()
    # Walk to the nearest existing ancestor so the check works before the
    # directory has ever been created.
    probe = target
    while probe and not os.path.exists(probe):
        parent = os.path.dirname(probe)
        if parent == probe:
            break
        probe = parent
    if not probe or not os.path.exists(probe):
        return DiskStatus(path=target, total_bytes=0, free_bytes=0,
                          error="no_existing_path")
    try:
        usage = shutil.disk_usage(probe)
    except OSError as exc:
        logger.warning("disk_usage_failed path=%s error=%s", target, type(exc).__name__)
        return DiskStatus(path=target, total_bytes=0, free_bytes=0,
                          error=type(exc).__name__)
    return DiskStatus(path=target, total_bytes=int(usage.total),
                      free_bytes=int(usage.free))


def installed_ram_bytes() -> int | None:
    """Physically installed RAM in bytes, or None when it cannot be read.

    Reports installed capacity, not currently-available capacity: the
    question the first-run check answers is "can this machine host a local
    model at all", not "is there room right now".
    """
    try:
        if sys.platform == "win32":
            # GetPhysicallyInstalledSystemMemory returns kilobytes.
            kb = ctypes.c_ulonglong(0)
            ok = ctypes.windll.kernel32.GetPhysicallyInstalledSystemMemory(
                ctypes.byref(kb)
            )
            if not ok or kb.value == 0:
                return None
            return int(kb.value) * 1024
        page = os.sysconf("SC_PAGE_SIZE")
        pages = os.sysconf("SC_PHYS_PAGES")
        if page <= 0 or pages <= 0:
            return None
        return int(page) * int(pages)
    except (OSError, AttributeError, ValueError) as exc:
        logger.warning("ram_probe_failed platform=%s error=%s",
                       sys.platform, type(exc).__name__)
        return None


# Smallest RAM we will let a user start a local model download against.
#
# This is a *policy floor for the download*, not a fabricated model size: it
# is the amount of memory a small local model plus the Ollama server needs to
# make progress at all. It is deliberately the only constant in this module,
# it is stated here rather than buried in a caller, and it never substitutes
# for a real model size in any size calculation.
MIN_DOWNLOAD_RAM_BYTES = 4 * 1024 * 1024 * 1024


@dataclass(frozen=True)
class ResourceCheck:
    """Result of the pre-download system check."""

    ram_bytes: int | None
    ram_sufficient: bool | None
    disk: DiskStatus
    blocking: bool
    code: str | None
    guidance: str | None


def check_for_model_download(required_bytes: int | None) -> ResourceCheck:
    """Decide whether a model download may start on this machine.

    `required_bytes` is the real download size when known and None when it
    is not yet known — never a guess. A blocking result carries a stable
    code and an actionable sentence, per the error-handling rules.
    """
    ram = installed_ram_bytes()
    disk = disk_status()

    if ram is None:
        # Uncertain measurement is reported as uncertain, not as failure.
        ram_sufficient = None
    else:
        ram_sufficient = ram >= MIN_DOWNLOAD_RAM_BYTES

    if not disk.available:
        return ResourceCheck(
            ram_bytes=ram, ram_sufficient=ram_sufficient, disk=disk,
            blocking=True, code="DISK_CHECK_FAILED",
            guidance=(
                "Alfred could not read the free space on this drive, so it "
                "will not start a download that might fill it. Check the "
                "drive and try again."
            ),
        )

    if required_bytes is not None and disk.free_bytes < required_bytes:
        shortfall = required_bytes - disk.free_bytes
        return ResourceCheck(
            ram_bytes=ram, ram_sufficient=ram_sufficient, disk=disk,
            blocking=True, code="INSUFFICIENT_DISK_SPACE",
            guidance=(
                f"Not enough free space to download this model. "
                f"About {human_bytes(shortfall)} more is needed on "
                f"{disk.path}."
            ),
        )

    if ram_sufficient is False:
        return ResourceCheck(
            ram_bytes=ram, ram_sufficient=False, disk=disk,
            blocking=True, code="INSUFFICIENT_MEMORY",
            guidance=(
                "This machine has less than 4 GB of installed memory, which "
                "is not enough to run a local model. The mailbox works "
                "without it."
            ),
        )

    return ResourceCheck(
        ram_bytes=ram, ram_sufficient=ram_sufficient, disk=disk,
        blocking=False, code=None, guidance=None,
    )


def human_bytes(value: int | None) -> str:
    """Format bytes with binary units, consistently across every surface."""
    if value is None:
        return "unknown size"
    if value < 1024:
        return f"{value} B"
    units = ("KB", "MB", "GB", "TB")
    size = float(value)
    for unit in units:
        size /= 1024.0
        if size < 1024.0 or unit == units[-1]:
            return f"{size:.1f} {unit}"
    return f"{size:.1f} TB"
