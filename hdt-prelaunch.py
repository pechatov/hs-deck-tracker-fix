#!/usr/bin/env python3
"""Keep the supported HDT build working under Wine/XWayland.

Wine renders a fully transparent WPF background as opaque black. HDT already
contains an optional translucent debug background; changing its alpha to the
smallest non-zero value avoids that Wine bug while leaving overlay widgets at
full opacity.

The current upstream release also lacks Wine-compatible Battlegrounds buttons,
Wine can report virtual-desktop-sized game bounds during minimize/restore,
animated card tooltips can leave opaque black dirty rectangles, and fully empty
opacity-mask regions over Hearthstone cards are rendered black. Wine can also
leave a non-interactive Battlegrounds board region owned by the overlay. Before launch,
reject an update without all local markers and atomically restore the known-good
installation snapshot. Accepted local builds still receive the transparency
patch.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import struct
import sys
from pathlib import Path


WINE_PREFIX = Path(
    os.environ.get(
        "HDT_WINE_PREFIX",
        str(Path.home() / "Games/hs/battlenet"),
    )
)
HDT_DIR = Path(
    os.environ.get(
        "HDT_DIR",
        str(
            WINE_PREFIX
            / "drive_c/users/steamuser/AppData/Local/HearthstoneDeckTracker/"
            "Hearthstone Deck Tracker"
        ),
    )
)
EXE = HDT_DIR / "Hearthstone Deck Tracker.exe"
SCRY = HDT_DIR / "untapped-scry-dotnet.dll"
CONFIG = Path(
    os.environ.get(
        "HDT_CONFIG",
        str(
            WINE_PREFIX
            / "drive_c/users/steamuser/AppData/Roaming/"
            "HearthstoneDeckTracker/config.xml"
        ),
    )
)
BATTLE_NET_CONFIG = Path(
    os.environ.get(
        "BATTLE_NET_CONFIG",
        str(
            WINE_PREFIX
            / "drive_c/users/steamuser/AppData/Roaming/Battle.net/"
            "Battle.net.config"
        ),
    )
)
BACKUP_ROOT = Path(
    os.environ.get(
        "HDT_BACKUP_ROOT",
        str(Path.home() / ".local/share/lutris/backups/hdt-overlay"),
    )
)
WORKING_SNAPSHOT = Path(
    os.environ.get(
        "HDT_WORKING_SNAPSHOT",
        str(BACKUP_ROOT / "working-current-wine"),
    )
)
UPDATE_PIN = BACKUP_ROOT / "PIN_AUTOMATIC_UPDATES"
UPDATE_ATTEMPT = BACKUP_ROOT / "ONE_SHOT_UPDATE_ATTEMPT"

# Both strings have the same UTF-16LE length, so no PE offsets are changed.
ORIGINAL_BRUSH = "#4C0000FF".encode("utf-16le")
WINE_BRUSH = "#01000000".encode("utf-16le")
BUTTON_FIX_MARKER = (
    b"Hearthstone_Deck_Tracker.Controls.Overlay.Battlegrounds.OverlayButton"
)
FIXED_POSITION_MARKER = "HDT_WINE_FIXED_OVERLAY_2730X1091".encode("utf-16le")
TOOLTIP_FIX_MARKER = b"HDT_WINE_TOOLTIP_NO_ZERO_STATE"
OPACITY_MASK_FIX_MARKER = "HDT_WINE_OPACITY_MASK_DISABLED".encode("utf-16le")
CLICKTHROUGH_FIX_MARKER = "HDT_WINE_BATTLEGROUNDS_CLICKTHROUGH_ZONE".encode("utf-16le")
TOOLTIP_RUNTIME_FILES = (
    "System.Buffers.dll",
    "System.Memory.dll",
    "System.Numerics.Vectors.dll",
    "System.Resources.Extensions.dll",
    "System.Runtime.CompilerServices.Unsafe.dll",
)


def keep_battle_net_open_during_game() -> bool:
    """Keep Battle.net alive so the launcher can close it after Hearthstone."""
    if not BATTLE_NET_CONFIG.is_file():
        print(
            f"Battle.net lifecycle: config not found: {BATTLE_NET_CONFIG}",
            file=sys.stderr,
        )
        return False

    try:
        config = json.loads(BATTLE_NET_CONFIG.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        print(
            f"Battle.net lifecycle: could not read config: {error}",
            file=sys.stderr,
        )
        return False

    client = config.setdefault("Client", {})
    if not isinstance(client, dict):
        print(
            "Battle.net lifecycle: Client config has an unexpected format",
            file=sys.stderr,
        )
        return False
    if client.get("GameLaunchWindowBehavior") == "0":
        print("Battle.net lifecycle: launcher will stay open during Hearthstone")
        return True

    client["GameLaunchWindowBehavior"] = "0"
    temporary = BATTLE_NET_CONFIG.with_name(
        f".{BATTLE_NET_CONFIG.name}.lifecycle.tmp"
    )
    try:
        temporary.write_text(
            json.dumps(config, ensure_ascii=False, indent=4) + "\n",
            encoding="utf-8",
        )
        shutil.copymode(BATTLE_NET_CONFIG, temporary)
        os.replace(temporary, BATTLE_NET_CONFIG)
    except OSError as error:
        temporary.unlink(missing_ok=True)
        print(
            f"Battle.net lifecycle: could not update config: {error}",
            file=sys.stderr,
        )
        return False

    print("Battle.net lifecycle: launcher will stay open during Hearthstone")
    return True


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def tooltip_runtime_present(root: Path = HDT_DIR) -> bool:
    return all((root / name).is_file() for name in TOOLTIP_RUNTIME_FILES)


def set_auto_updates(enabled: bool) -> bool:
    """Toggle HDT's own updater without reformatting config.xml."""
    if not CONFIG.is_file():
        print(f"HDT update guard: config not found: {CONFIG}", file=sys.stderr)
        return False

    data = CONFIG.read_bytes()
    current = b"<CheckForUpdates>true</CheckForUpdates>"
    disabled = b"<CheckForUpdates>false</CheckForUpdates>"
    replacement = current if enabled else disabled
    opposite = disabled if enabled else current

    if replacement in data:
        return True
    if data.count(opposite) != 1:
        print(
            "HDT update guard: CheckForUpdates has an unexpected format; "
            "leaving config unchanged",
            file=sys.stderr,
        )
        return False

    temporary = CONFIG.with_name(f".{CONFIG.name}.update-guard.tmp")
    temporary.write_bytes(data.replace(opposite, replacement, 1))
    shutil.copymode(CONFIG, temporary)
    os.replace(temporary, CONFIG)
    return True


def force_software_rendering() -> bool:
    """Disable WPF hardware rendering, which is unstable under Wine."""
    if not CONFIG.is_file():
        print(f"HDT rendering guard: config not found: {CONFIG}", file=sys.stderr)
        return False

    data = CONFIG.read_bytes()
    hardware = b"<UseHardwareAcceleration>true</UseHardwareAcceleration>"
    software = b"<UseHardwareAcceleration>false</UseHardwareAcceleration>"
    if software in data:
        return True
    if data.count(hardware) != 1:
        print(
            "HDT rendering guard: UseHardwareAcceleration has an unexpected "
            "format; leaving config unchanged",
            file=sys.stderr,
        )
        return False

    temporary = CONFIG.with_name(f".{CONFIG.name}.rendering-guard.tmp")
    temporary.write_bytes(data.replace(hardware, software, 1))
    shutil.copymode(CONFIG, temporary)
    os.replace(temporary, CONFIG)
    print("HDT rendering guard: software rendering forced for Wine stability")
    return True


def pin_auto_updates() -> bool:
    BACKUP_ROOT.mkdir(parents=True, exist_ok=True)
    UPDATE_ATTEMPT.unlink(missing_ok=True)
    UPDATE_PIN.write_text(
        "Pinned until an HDT build passes all local Wine overlay checks.\n",
        encoding="utf-8",
    )
    return set_auto_updates(False)


def unpin_auto_updates() -> bool:
    if not EXE.is_file() or not set_auto_updates(True):
        return False
    BACKUP_ROOT.mkdir(parents=True, exist_ok=True)
    UPDATE_PIN.unlink(missing_ok=True)
    UPDATE_ATTEMPT.write_text(
        f"{sha256(EXE.read_bytes())}\narmed\n",
        encoding="utf-8",
    )
    return True


def manage_one_shot_update() -> bool:
    """Allow one HDT launch to check/update, then automatically pin again."""
    if UPDATE_PIN.exists():
        return set_auto_updates(False)
    if not UPDATE_ATTEMPT.is_file():
        return True

    try:
        base_hash, state = UPDATE_ATTEMPT.read_text(encoding="utf-8").splitlines()[:2]
    except (OSError, ValueError, IndexError):
        print("HDT update guard: invalid one-shot update marker; pinning", file=sys.stderr)
        return pin_auto_updates()

    current_hash = sha256(EXE.read_bytes())
    if current_hash != base_hash:
        print("HDT update guard: detected the result of a one-shot update")
        return True
    if state == "armed":
        UPDATE_ATTEMPT.write_text(f"{base_hash}\nattempted\n", encoding="utf-8")
        return set_auto_updates(True)

    print("HDT update guard: no update was installed; pinning again")
    return pin_auto_updates()


def one_shot_update_installed() -> bool:
    if not UPDATE_ATTEMPT.is_file() or not EXE.is_file():
        return False
    try:
        base_hash = UPDATE_ATTEMPT.read_text(encoding="utf-8").splitlines()[0]
    except (OSError, IndexError):
        return False
    return sha256(EXE.read_bytes()) != base_hash


def snapshot_is_valid() -> bool:
    snapshot_exe = WORKING_SNAPSHOT / EXE.name
    if not snapshot_exe.is_file():
        return False
    try:
        data = snapshot_exe.read_bytes()
        return (
            BUTTON_FIX_MARKER in data
            and FIXED_POSITION_MARKER in data
            and TOOLTIP_FIX_MARKER in data
            and OPACITY_MASK_FIX_MARKER in data
            and CLICKTHROUGH_FIX_MARKER in data
            and tooltip_runtime_present(WORKING_SNAPSHOT)
            and transparency_patch_supported(data)
        )
    except OSError:
        return False


def restore_working_snapshot(candidate_data: bytes) -> bool:
    """Atomically replace an incompatible update with the known-good tree."""
    if os.environ.get("HDT_ALLOW_UNPATCHED_UPDATE") == "1":
        print(
            "HDT update guard: allowing an update without the Wine button fix "
            "because HDT_ALLOW_UNPATCHED_UPDATE=1",
            file=sys.stderr,
        )
        return True

    if not snapshot_is_valid():
        print(
            f"HDT update guard: incompatible installation detected, but the "
            f"working snapshot is missing or invalid: {WORKING_SNAPSHOT}",
            file=sys.stderr,
        )
        return False

    digest = sha256(candidate_data)
    rejected_backup = BACKUP_ROOT / "rejected-updates" / digest
    rejected_backup.parent.mkdir(parents=True, exist_ok=True)
    if not rejected_backup.exists():
        shutil.copytree(HDT_DIR, rejected_backup, symlinks=True)

    parent = HDT_DIR.parent
    staging = parent / f".{HDT_DIR.name}.compat-restore-{os.getpid()}"
    displaced = parent / f".{HDT_DIR.name}.incompatible-{digest[:12]}"
    shutil.rmtree(staging, ignore_errors=True)
    shutil.rmtree(displaced, ignore_errors=True)
    shutil.copytree(WORKING_SNAPSHOT, staging, symlinks=True)

    os.replace(HDT_DIR, displaced)
    try:
        os.replace(staging, HDT_DIR)
    except Exception:
        os.replace(displaced, HDT_DIR)
        shutil.rmtree(staging, ignore_errors=True)
        raise
    shutil.rmtree(displaced, ignore_errors=True)

    restored = EXE.read_bytes()
    if (
        BUTTON_FIX_MARKER not in restored
        or FIXED_POSITION_MARKER not in restored
        or TOOLTIP_FIX_MARKER not in restored
        or OPACITY_MASK_FIX_MARKER not in restored
        or CLICKTHROUGH_FIX_MARKER not in restored
        or not tooltip_runtime_present()
    ):
        print("HDT update guard: snapshot restore verification failed", file=sys.stderr)
        return False

    pin_auto_updates()
    print(
        "HDT update guard: the installed update did not pass the Wine "
        "compatibility checks; saved it under rejected-updates and "
        "restored the last known-good build"
    )
    return True


def transparency_patch_supported(data: bytes) -> bool:
    return (
        data.count(ORIGINAL_BRUSH) == 1 and data.count(WINE_BRUSH) == 0
    ) or (
        data.count(ORIGINAL_BRUSH) == 0 and data.count(WINE_BRUSH) == 1
    )


def ensure_wine_compatibility() -> bool:
    data = EXE.read_bytes()
    exe_machine = pe_machine(EXE)
    scry_machine = pe_machine(SCRY)
    runtime_matches = not (exe_machine and scry_machine) or exe_machine == scry_machine
    if (
        BUTTON_FIX_MARKER in data
        and FIXED_POSITION_MARKER in data
        and TOOLTIP_FIX_MARKER in data
        and OPACITY_MASK_FIX_MARKER in data
        and CLICKTHROUGH_FIX_MARKER in data
        and tooltip_runtime_present()
        and transparency_patch_supported(data)
        and runtime_matches
    ):
        print("HDT update guard: Wine compatibility checks passed")
        return True
    return restore_working_snapshot(data)


def pe_machine(path: Path) -> int | None:
    try:
        with path.open("rb") as stream:
            header = stream.read(64)
            pe_offset = struct.unpack_from("<I", header, 0x3C)[0]
            stream.seek(pe_offset)
            signature_and_machine = stream.read(6)
        if signature_and_machine[:4] != b"PE\0\0":
            return None
        return struct.unpack_from("<H", signature_and_machine, 4)[0]
    except (OSError, IndexError, struct.error):
        return None


def validate_runtime() -> None:
    exe_machine = pe_machine(EXE)
    scry_machine = pe_machine(SCRY)
    if exe_machine and scry_machine and exe_machine != scry_machine:
        print(
            "HDT warning: untapped-scry-dotnet architecture does not match HDT; "
            "Battlegrounds detection will not work.",
            file=sys.stderr,
        )


def patch_overlay() -> None:
    data = EXE.read_bytes()
    original_count = data.count(ORIGINAL_BRUSH)
    patched_count = data.count(WINE_BRUSH)

    if original_count == 0 and patched_count == 1:
        print("HDT Wine overlay patch: already applied")
        return
    if original_count != 1:
        print(
            "HDT Wine overlay patch: this HDT version has a different overlay "
            "implementation; leaving the executable unchanged",
            file=sys.stderr,
        )
        return

    BACKUP_ROOT.mkdir(parents=True, exist_ok=True)
    digest = sha256(data)
    backup = BACKUP_ROOT / f"Hearthstone Deck Tracker-{digest}.exe"
    if not backup.exists():
        shutil.copy2(EXE, backup)

    patched = data.replace(ORIGINAL_BRUSH, WINE_BRUSH, 1)
    temporary = EXE.with_name(f".{EXE.name}.overlay-patch.tmp")
    temporary.write_bytes(patched)
    shutil.copymode(EXE, temporary)
    os.replace(temporary, EXE)
    print("HDT Wine overlay patch: applied")


def refresh_working_snapshot() -> bool:
    """Promote an accepted, fully patched release to the rollback snapshot."""
    data = EXE.read_bytes()
    exe_machine = pe_machine(EXE)
    scry_machine = pe_machine(SCRY)
    runtime_matches = not (exe_machine and scry_machine) or exe_machine == scry_machine
    if (
        BUTTON_FIX_MARKER not in data
        or FIXED_POSITION_MARKER not in data
        or TOOLTIP_FIX_MARKER not in data
        or OPACITY_MASK_FIX_MARKER not in data
        or CLICKTHROUGH_FIX_MARKER not in data
        or not tooltip_runtime_present()
        or not transparency_patch_supported(data)
        or WINE_BRUSH not in data
        or not runtime_matches
    ):
        print(
            "HDT update guard: refusing to snapshot an installation that did "
            "not pass all Wine checks",
            file=sys.stderr,
        )
        return False

    snapshot_exe = WORKING_SNAPSHOT / EXE.name
    if snapshot_exe.is_file() and sha256(snapshot_exe.read_bytes()) == sha256(data):
        return True

    BACKUP_ROOT.mkdir(parents=True, exist_ok=True)
    staging = BACKUP_ROOT / f".{WORKING_SNAPSHOT.name}.refresh-{os.getpid()}"
    previous = BACKUP_ROOT / f".{WORKING_SNAPSHOT.name}.previous-{os.getpid()}"
    shutil.rmtree(staging, ignore_errors=True)
    shutil.rmtree(previous, ignore_errors=True)
    shutil.copytree(HDT_DIR, staging, symlinks=True)

    had_previous = WORKING_SNAPSHOT.exists()
    if had_previous:
        os.replace(WORKING_SNAPSHOT, previous)
    try:
        os.replace(staging, WORKING_SNAPSHOT)
    except Exception:
        if had_previous:
            os.replace(previous, WORKING_SNAPSHOT)
        shutil.rmtree(staging, ignore_errors=True)
        raise
    shutil.rmtree(previous, ignore_errors=True)
    print("HDT update guard: refreshed the known-good Wine snapshot")
    return True


def print_status() -> None:
    if not EXE.is_file():
        print(f"executable: missing ({EXE})")
        return
    data = EXE.read_bytes()
    config = CONFIG.read_bytes() if CONFIG.is_file() else b""
    print(f"executable: {sha256(data)}")
    print(f"Wine button fix: {'yes' if BUTTON_FIX_MARKER in data else 'no'}")
    print(
        "fixed overlay geometry: "
        + ("yes" if FIXED_POSITION_MARKER in data else "no")
    )
    print(
        "Wine tooltip zero-state fix: "
        + ("yes" if TOOLTIP_FIX_MARKER in data else "no")
    )
    print(
        "Wine window opacity-mask disabled: "
        + ("yes" if OPACITY_MASK_FIX_MARKER in data else "no")
    )
    print(
        "Wine Battlegrounds click-through zone: "
        + ("yes" if CLICKTHROUGH_FIX_MARKER in data else "no")
    )
    print(
        "tooltip resource runtime: "
        + ("yes" if tooltip_runtime_present() else "no")
    )
    print(f"Wine transparency fix: {'yes' if WINE_BRUSH in data else 'no'}")
    print(
        "known transparency layout: "
        + ("yes" if transparency_patch_supported(data) else "no")
    )
    print(f"working snapshot: {'valid' if snapshot_is_valid() else 'missing/invalid'}")
    if UPDATE_PIN.exists():
        update_status = "pinned by Wine compatibility guard"
    elif UPDATE_ATTEMPT.exists():
        update_status = "enabled for one update attempt"
    elif b"<CheckForUpdates>true</CheckForUpdates>" in config:
        update_status = "enabled"
    else:
        update_status = "disabled in HDT config"
    print(f"automatic updates: {update_status}")
    if b"<UseHardwareAcceleration>false</UseHardwareAcceleration>" in config:
        rendering_status = "software (Wine stability guard)"
    elif b"<UseHardwareAcceleration>true</UseHardwareAcceleration>" in config:
        rendering_status = "hardware (unsafe under Wine)"
    else:
        rendering_status = "unknown"
    print(f"rendering mode: {rendering_status}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--status", action="store_true")
    group.add_argument("--enable-updates", action="store_true")
    group.add_argument("--disable-updates", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.status:
        print_status()
        return 0
    if args.enable_updates:
        if unpin_auto_updates():
            print("HDT automatic updates: enabled for the next official update")
            return 0
        return 1
    if args.disable_updates:
        if pin_auto_updates():
            print("HDT automatic updates: pinned to the working Wine build")
            return 0
        return 1

    if not keep_battle_net_open_during_game():
        return 1
    if not force_software_rendering():
        return 1
    if not EXE.is_file():
        print(f"HDT Wine overlay patch: executable not found: {EXE}", file=sys.stderr)
        return 0
    if not manage_one_shot_update():
        return 1
    if not ensure_wine_compatibility():
        return 1
    validate_runtime()
    patch_overlay()
    if not refresh_working_snapshot():
        return 1
    if one_shot_update_installed() and not pin_auto_updates():
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
