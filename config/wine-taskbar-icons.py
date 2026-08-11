#!/usr/bin/env python3
"""Keep Hearthstone/HDT XWayland identities and geometry stable.

UMU/Proton assigns ``steam_app_default`` to both Hearthstone and HDT. Waybar's
wlr/taskbar resolves icons by that shared app ID, so it cannot distinguish the
two windows. Keep their WM_CLASS values mapped from their exact titles, mark
Wine's empty 160x20 helper as skip-taskbar, and keep the game/HDT windows out
of fullscreen with the verified DP-1 geometry.
"""

from __future__ import annotations

import fcntl
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path


WINDOWS = {
    "^Hearthstone$": "hearthstone-hand-drawn",
    "^Hearthstone Deck Tracker$": "hearthstone-deck-tracker",
}

WINE_CLASS = "^steam_app_default$"
EMPTY_HELPER_SIZE = (160, 20)
PROTECTED_WINDOWS = {
    "Hearthstone": {"workspace": "5", "floating": False},
    "HearthstoneOverlay": {"workspace": "5", "floating": True},
    "Hearthstone Deck Tracker": {"workspace": "3", "floating": True},
}
X11_GEOMETRIES = {
    "^HearthstoneOverlay$": (3453, 62, 3412, 1363),
    "^Hearthstone Deck Tracker$": (3612, 72, 1200, 675),
}
LUTRIS_CLASSES = {"net.lutris.Lutris", "lutris"}
BATTLE_NET_FALLBACK_WORKSPACE = "3"
HEARTHSTONE_PROCESS = "hearthstone.exe"
HDT_PROCESS = "hearthstone deck tracker.exe"
HDT_AUTOCLOSE_DELAY_SECONDS = 6.0
HDT_FORCE_CLOSE_SECONDS = 15.0
POLL_SECONDS = 1.0
_running = True


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
    )


def log_autoclose(message: str) -> None:
    runtime_dir = Path(os.environ.get("XDG_RUNTIME_DIR", "/tmp"))
    try:
        with (runtime_dir / "hdt-autoclose.log").open("a", encoding="utf-8") as log:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            log.write(f"{timestamp} {message}\n")
    except OSError:
        pass


def update_windows() -> None:
    for title_pattern, target_class in WINDOWS.items():
        result = run("xdotool", "search", "--name", title_pattern)
        if result.returncode != 0:
            continue

        for window_id in result.stdout.split():
            current = run("xdotool", "getwindowclassname", window_id)
            if current.returncode != 0 or current.stdout.strip() == target_class:
                continue
            run(
                "xdotool",
                "set_window",
                "--classname",
                target_class,
                "--class",
                target_class,
                window_id,
            )


def add_skip_taskbar(window_id: str) -> None:
    state = run("xprop", "-id", window_id, "_NET_WM_STATE")
    if "_NET_WM_STATE_SKIP_TASKBAR" in state.stdout:
        return
    atoms = []
    if "=" in state.stdout:
        atoms = [
            atom.strip()
            for atom in state.stdout.split("=", 1)[1].split(",")
            if atom.strip().startswith("_NET_WM_STATE_")
        ]
    atoms.append("_NET_WM_STATE_SKIP_TASKBAR")
    run(
        "xprop",
        "-id",
        window_id,
        "-f",
        "_NET_WM_STATE",
        "32a",
        "-set",
        "_NET_WM_STATE",
        ", ".join(atoms),
    )


def hide_empty_wine_helpers() -> None:
    """Hide the stable Wine helper without touching real or overlay windows."""
    result = run("xdotool", "search", "--class", WINE_CLASS)
    if result.returncode != 0:
        return

    for window_id in result.stdout.split():
        title = run("xdotool", "getwindowname", window_id)
        if title.returncode != 0 or title.stdout.rstrip("\n"):
            continue

        geometry = run("xdotool", "getwindowgeometry", "--shell", window_id)
        if geometry.returncode != 0:
            continue
        values = {}
        for line in geometry.stdout.splitlines():
            key, separator, value = line.partition("=")
            if separator and value.isdigit():
                values[key] = int(value)
        if (values.get("WIDTH"), values.get("HEIGHT")) != EMPTY_HELPER_SIZE:
            continue

        add_skip_taskbar(window_id)


def hide_overlay_from_taskbar() -> None:
    result = run("xdotool", "search", "--name", "^HearthstoneOverlay$")
    if result.returncode != 0:
        return
    for window_id in result.stdout.split():
        title = run("xdotool", "getwindowname", window_id)
        if title.returncode == 0 and title.stdout.strip() == "HearthstoneOverlay":
            add_skip_taskbar(window_id)


def parse_shell_geometry(output: str) -> dict[str, int]:
    values = {}
    for line in output.splitlines():
        key, separator, value = line.partition("=")
        if separator and value.lstrip("-").isdigit():
            values[key] = int(value)
    return values


def enforce_x11_geometry() -> None:
    """Undo external move/resize operations on the two fixed WPF windows."""
    for title_pattern, target in X11_GEOMETRIES.items():
        result = run("xdotool", "search", "--name", title_pattern)
        if result.returncode != 0:
            continue
        target_x, target_y, target_width, target_height = target
        for window_id in result.stdout.split():
            geometry = run("xdotool", "getwindowgeometry", "--shell", window_id)
            if geometry.returncode != 0:
                continue
            values = parse_shell_geometry(geometry.stdout)
            current = (
                values.get("X"),
                values.get("Y"),
                values.get("WIDTH"),
                values.get("HEIGHT"),
            )
            if current == target:
                continue
            # Do not use --sync here: a compositor fullscreen state can defer
            # the X11 configure request and make xdotool wait indefinitely.
            run("xdotool", "windowsize", window_id, str(target_width), str(target_height))
            run("xdotool", "windowmove", window_id, str(target_x), str(target_y))


def read_json(*args: str) -> object | None:
    result = run(*args)
    if result.returncode != 0:
        return None
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return None


def client_workspace(client: dict[str, object]) -> str | None:
    workspace = client.get("workspace")
    if not isinstance(workspace, dict):
        return None
    name = workspace.get("name")
    if not isinstance(name, str) or not name or name == "-99":
        return None
    return name


def process_command(pid: object) -> str:
    if not isinstance(pid, int) or pid <= 0:
        return ""
    try:
        return Path(f"/proc/{pid}/cmdline").read_bytes().replace(b"\0", b" ").decode(
            errors="replace"
        )
    except OSError:
        return ""


def is_battle_net(client: dict[str, object]) -> bool:
    """Recognize the launcher without confusing it with Hearthstone/HDT."""
    title = str(client.get("title") or "").casefold()
    initial_title = str(client.get("initialTitle") or "").casefold()
    window_class = str(client.get("class") or "").casefold()
    initial_class = str(client.get("initialClass") or "").casefold()
    wine_class = window_class == "steam_app_default" or initial_class == "steam_app_default"
    class_mentions_battle_net = "battle.net" in window_class or "battle.net" in initial_class
    title_mentions_battle_net = title.startswith("battle.net") or initial_title.startswith(
        "battle.net"
    )
    if title_mentions_battle_net and (wine_class or class_mentions_battle_net):
        return True

    command = process_command(client.get("pid")).casefold()
    return (
        ("battle.net.exe" in command or "battle.net launcher.exe" in command)
        and "battle.net helper.exe" not in command
        and "agent.exe" not in command
    )


def lutris_workspace(clients: list[object]) -> str:
    candidates = []
    for client in clients:
        if not isinstance(client, dict) or not client.get("mapped", True):
            continue
        window_class = str(client.get("class") or "")
        initial_class = str(client.get("initialClass") or "")
        if window_class not in LUTRIS_CLASSES and initial_class not in LUTRIS_CLASSES:
            continue
        workspace = client_workspace(client)
        if workspace is None:
            continue
        history = client.get("focusHistoryID")
        priority = history if isinstance(history, int) and history >= 0 else 1_000_000
        candidates.append((priority, workspace))
    if not candidates:
        return BATTLE_NET_FALLBACK_WORKSPACE
    return min(candidates)[1]


def sync_battle_net_workspace(clients: list[object]) -> None:
    target_workspace = lutris_workspace(clients)
    for client in clients:
        if not isinstance(client, dict) or not is_battle_net(client):
            continue
        address = client.get("address")
        if not isinstance(address, str) or client_workspace(client) == target_workspace:
            continue
        run(
            "hyprctl",
            "dispatch",
            "movetoworkspacesilent",
            f"{target_workspace},address:{address}",
        )


def process_is_live(pid: int) -> bool:
    """Reject Wine processes that exited but have not yet been reaped."""
    try:
        stat = Path(f"/proc/{pid}/stat").read_text(encoding="utf-8")
    except OSError:
        return False
    tail = stat.rsplit(")", 1)
    return len(tail) == 2 and tail[1].split() and tail[1].split()[0] != "Z"


def exact_executable_pids(executable_name: str) -> list[int]:
    """Find only the real Windows process, never a Lutris/UMU wrapper."""
    result: list[int] = []
    own_pid = os.getpid()
    for cmdline_path in Path("/proc").glob("[0-9]*/cmdline"):
        try:
            pid = int(cmdline_path.parent.name)
            if pid == own_pid or not process_is_live(pid):
                continue
            argv = cmdline_path.read_bytes().split(b"\0")
        except (OSError, ValueError):
            continue
        if not argv or not argv[0]:
            continue
        executable = (
            argv[0]
            .decode("utf-8", errors="replace")
            .replace("\\", "/")
            .rsplit("/", 1)[-1]
            .casefold()
        )
        if executable == executable_name:
            result.append(pid)
    return result


class HdtAutoCloser:
    """Close HDT only after a Hearthstone session observed by this guard ends."""

    def __init__(
        self,
        close_delay: float = HDT_AUTOCLOSE_DELAY_SECONDS,
        force_delay: float = HDT_FORCE_CLOSE_SECONDS,
    ) -> None:
        self.close_delay = close_delay
        self.force_delay = force_delay
        self.game_seen = False
        self.missing_since: float | None = None
        self.close_requested_at: float | None = None
        self.force_sent = False

    def reset(self) -> None:
        self.game_seen = False
        self.missing_since = None
        self.close_requested_at = None
        self.force_sent = False

    def observe(
        self, game_running: bool, hdt_running: bool, now: float | None = None
    ) -> str | None:
        timestamp = time.monotonic() if now is None else now

        if game_running:
            if not self.game_seen:
                log_autoclose("Hearthstone observed; auto-close armed")
            elif self.missing_since is not None:
                log_autoclose("Hearthstone returned; pending HDT close cancelled")
            self.game_seen = True
            self.missing_since = None
            self.close_requested_at = None
            self.force_sent = False
            return None

        if not hdt_running:
            if self.game_seen:
                log_autoclose("HDT is no longer running; lifecycle state reset")
            self.reset()
            return None

        # HDT started on its own, or is waiting for Battle.net to launch the
        # game. Never close it until Hearthstone has actually been observed.
        if not self.game_seen:
            return None

        if self.missing_since is None:
            self.missing_since = timestamp
            log_autoclose("Hearthstone stopped; HDT close grace period started")
            return None

        if self.close_requested_at is None:
            if timestamp - self.missing_since < self.close_delay:
                return None
            self.close_requested_at = timestamp
            log_autoclose("Requesting clean HDT shutdown via WM_CLOSE")
            return "close"

        if not self.force_sent and timestamp - self.close_requested_at >= self.force_delay:
            self.force_sent = True
            log_autoclose("Clean shutdown timed out; sending SIGTERM to HDT")
            return "terminate"
        return None


def request_clean_hdt_shutdown() -> None:
    result = run("xdotool", "search", "--name", "^Hearthstone Deck Tracker$")
    if result.returncode != 0:
        return
    for window_id in result.stdout.split():
        title = run("xdotool", "getwindowname", window_id)
        if title.returncode == 0 and title.stdout.strip() == "Hearthstone Deck Tracker":
            run("xdotool", "windowclose", window_id)


def manage_hdt_autoclose(clients: list[object], state: HdtAutoCloser) -> None:
    # XWayland can retain a dead Wine window. Process state is the reliable
    # lifecycle signal and avoids keeping HDT alive for a zombie Hearthstone.
    game_pids = exact_executable_pids(HEARTHSTONE_PROCESS)
    hdt_pids = exact_executable_pids(HDT_PROCESS)
    action = state.observe(bool(game_pids), bool(hdt_pids))
    if action == "close":
        request_clean_hdt_shutdown()
    elif action == "terminate":
        for pid in hdt_pids:
            run("kill", "-TERM", str(pid))


def clear_fullscreen(address: str) -> None:
    """Clear fullscreen on one window and restore the previously focused one."""
    active = read_json("hyprctl", "activewindow", "-j")
    previous = active.get("address") if isinstance(active, dict) else None
    if previous != address:
        run("hyprctl", "dispatch", "focuswindow", f"address:{address}")
    run("hyprctl", "dispatch", "fullscreenstate", "0", "0", "set")
    if previous and previous != address:
        run("hyprctl", "dispatch", "focuswindow", f"address:{previous}")


def normalize_hypr_windows() -> list[object]:
    """Keep protected windows on their workspaces and outside fullscreen."""
    clients = read_json("hyprctl", "clients", "-j")
    if not isinstance(clients, list):
        return []

    for client in clients:
        if not isinstance(client, dict):
            continue
        title = client.get("title")
        target = PROTECTED_WINDOWS.get(title)
        address = client.get("address")
        if target is None or not isinstance(address, str):
            continue

        if client.get("fullscreen", 0) or client.get("fullscreenClient", 0):
            clear_fullscreen(address)

        workspace = client.get("workspace")
        workspace_name = workspace.get("name") if isinstance(workspace, dict) else None
        if workspace_name != target["workspace"]:
            run(
                "hyprctl",
                "dispatch",
                "movetoworkspacesilent",
                f'{target["workspace"]},address:{address}',
            )

        floating = bool(client.get("floating"))
        if target["floating"] and not floating:
            run("hyprctl", "dispatch", "setfloating", f"address:{address}")
        elif not target["floating"] and floating:
            run("hyprctl", "dispatch", "settiled", f"address:{address}")

    # Battle.net follows the Lutris window, while Hearthstone remains governed
    # exclusively by PROTECTED_WINDOWS above and therefore stays on workspace 5.
    sync_battle_net_workspace(clients)
    return clients


def safe_fullscreen_toggle() -> int:
    """Replacement for Super+F that protects the HDT layout."""
    active = read_json("hyprctl", "activewindow", "-j")
    if not isinstance(active, dict):
        return 1
    if active.get("title") in PROTECTED_WINDOWS:
        address = active.get("address")
        if isinstance(address, str) and (
            active.get("fullscreen", 0) or active.get("fullscreenClient", 0)
        ):
            clear_fullscreen(address)
        normalize_hypr_windows()
        enforce_x11_geometry()
        return 0
    run("hyprctl", "dispatch", "fullscreen", "0")
    return 0


def stop(_signum: int, _frame: object) -> None:
    global _running
    _running = False


def main() -> int:
    if "--toggle-fullscreen" in sys.argv[1:]:
        return safe_fullscreen_toggle()

    runtime_dir = Path(os.environ.get("XDG_RUNTIME_DIR", "/tmp"))
    lock = (runtime_dir / "wine-taskbar-icons.lock").open("w")
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        return 0

    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    hdt_auto_closer = HdtAutoCloser()

    while _running:
        update_windows()
        hide_empty_wine_helpers()
        hide_overlay_from_taskbar()
        clients = normalize_hypr_windows()
        enforce_x11_geometry()
        manage_hdt_autoclose(clients, hdt_auto_closer)
        time.sleep(POLL_SECONDS)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
