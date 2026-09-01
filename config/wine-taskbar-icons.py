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

try:
    from Xlib import X as _X
    from Xlib import Xutil as _Xutil
    from Xlib import display as _xdisplay
except ImportError:
    _X = None


WINDOWS = {
    "^Hearthstone$": "hearthstone-hand-drawn",
    "^Hearthstone Deck Tracker$": "hearthstone-deck-tracker",
}

HDT_MAIN_TITLE = "Hearthstone Deck Tracker"
HDT_MAIN_TITLE_PATTERN = f"^{HDT_MAIN_TITLE}$"
WINE_CLASS = "^steam_app_default$"
EMPTY_HELPER_SIZE = (160, 20)
PROTECTED_WINDOWS = {
    "Hearthstone": {"workspace": "5", "floating": False},
    "HearthstoneOverlay": {"workspace": "5", "floating": True},
    "Hearthstone Deck Tracker": {"workspace": "3", "floating": True},
}
GAME_TITLE_PATTERN = "^Hearthstone$"
OVERLAY_TITLE_PATTERN = "^HearthstoneOverlay$"
HDT_MAIN_X11_OFFSET = (159, 10)
HDT_MAIN_X11_SIZE = (1200, 675)
LUTRIS_CLASSES = {"net.lutris.Lutris", "lutris"}
BATTLE_NET_FALLBACK_WORKSPACE = "3"
HEARTHSTONE_PROCESS = "hearthstone.exe"
HDT_PROCESS = "hearthstone deck tracker.exe"
HDT_AUTOCLOSE_DELAY_SECONDS = 6.0
HDT_FORCE_CLOSE_SECONDS = 15.0
HDT_RECOVERY_DELAY_SECONDS = 3.0
HDT_RESTART = Path.home() / ".local/bin/restart-hs-overlay"
RUNTIME_DIR = Path(os.environ.get("XDG_RUNTIME_DIR", "/tmp"))
HIDDEN_X11_STATE_PATH = RUNTIME_DIR / "wine-taskbar-icons-hidden-x11.json"
POLL_SECONDS = 1.0
_running = True
_hidden_workspace_x11_windows: dict[str, dict[str, object]] = {}


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


_x_display = None
_overlay_hint_applied: set[int] = set()


def _get_x_display():
    global _x_display
    if _X is None:
        return None
    if _x_display is None:
        try:
            _x_display = _xdisplay.Display()
        except Exception:
            _x_display = None
    return _x_display


def _drop_x_display() -> None:
    global _x_display
    if _x_display is not None:
        try:
            _x_display.close()
        except Exception:
            pass
    _x_display = None


def _find_x11_windows_by_exact_title(pattern: str, title: str) -> list[int]:
    result = run("xdotool", "search", "--name", pattern)
    if result.returncode != 0:
        return []
    matches = []
    for window_id in result.stdout.split():
        name = run("xdotool", "getwindowname", window_id)
        if name.returncode == 0 and name.stdout.strip() == title:
            matches.append(int(window_id))
    return matches


def enforce_overlay_no_input_hint() -> None:
    """Keep the X11 keyboard away from the transparent overlay.

    Wine publishes HearthstoneOverlay with WM_HINTS input=True even though the
    window sets WS_EX_NOACTIVATE. On click Hyprland's XWM then moves the X
    input focus to the overlay, which silently eats Battle.net chat typing
    while the click itself still reaches Hearthstone through the empty input
    shape. Forcing the ICCCM "No Input" model (InputHint flag set, input=0)
    makes Hyprland skip xcb_set_input_focus for the overlay: the X keyboard
    stays on Hearthstone, while the overlay still receives pointer clicks and
    is still raised in the X stacking order on focus (unlike the rolled-back
    no_focus window rule, which broke HDT panel clicks).

    Wine may rewrite WM_HINTS at any time, so the hint is re-asserted every
    cycle. If the overlay somehow already holds the X input focus (e.g. it was
    focused before this guard started), the focus is handed back to the game.
    """
    disp = _get_x_display()
    if disp is None:
        return
    overlay_ids = _find_x11_windows_by_exact_title(
        OVERLAY_TITLE_PATTERN, "HearthstoneOverlay"
    )
    if not overlay_ids:
        _overlay_hint_applied.clear()
        return
    try:
        for xid in overlay_ids:
            window = disp.create_resource_object("window", xid)
            hints = window.get_wm_hints()
            already_no_input = (
                hints is not None
                and hints.flags & _Xutil.InputHint
                and not hints.input
            )
            if already_no_input:
                continue
            if hints is None:
                window.set_wm_hints(flags=_Xutil.InputHint, input=0)
            else:
                hints.flags |= _Xutil.InputHint
                hints.input = 0
                window.set_wm_hints(hints)
            disp.sync()
            if xid not in _overlay_hint_applied:
                log_autoclose(
                    f"overlay {xid}: forced WM_HINTS input=False (chat focus fix)"
                )
                _overlay_hint_applied.add(xid)
        _overlay_hint_applied.intersection_update(overlay_ids)
        _release_stale_overlay_x_focus(disp, overlay_ids)
    except Exception:
        _drop_x_display()


def _release_stale_overlay_x_focus(disp, overlay_ids: list[int]) -> None:
    focus_id = getattr(disp.get_input_focus().focus, "id", None)
    if focus_id not in overlay_ids:
        return
    for game_id in _find_x11_windows_by_exact_title(GAME_TITLE_PATTERN, "Hearthstone"):
        game = disp.create_resource_object("window", game_id)
        disp.set_input_focus(game, _X.RevertToPointerRoot, _X.CurrentTime)
        disp.sync()
        log_autoclose(
            f"overlay {focus_id}: released stale X input focus to Hearthstone {game_id}"
        )
        return


def parse_shell_geometry(output: str) -> dict[str, int]:
    values = {}
    for line in output.splitlines():
        key, separator, value = line.partition("=")
        if separator and value.lstrip("-").isdigit():
            values[key] = int(value)
    return values


def enforce_x11_geometry() -> None:
    """Place WPF windows relative to Hearthstone's current X11 rectangle."""
    game_result = run("xdotool", "search", "--name", GAME_TITLE_PATTERN)
    if game_result.returncode != 0:
        return
    game_geometry: dict[str, int] | None = None
    for game_window_id in game_result.stdout.split():
        title = run("xdotool", "getwindowname", game_window_id)
        if title.returncode != 0 or title.stdout.strip() != "Hearthstone":
            continue
        geometry = run("xdotool", "getwindowgeometry", "--shell", game_window_id)
        if geometry.returncode == 0:
            game_geometry = parse_shell_geometry(geometry.stdout)
            break
    if game_geometry is None:
        return

    game_x = game_geometry.get("X")
    game_y = game_geometry.get("Y")
    game_width = game_geometry.get("WIDTH")
    game_height = game_geometry.get("HEIGHT")
    if not all(
        isinstance(value, int)
        for value in (game_x, game_y, game_width, game_height)
    ):
        return

    main_offset_x, main_offset_y = HDT_MAIN_X11_OFFSET
    main_width, main_height = HDT_MAIN_X11_SIZE
    targets = {
        OVERLAY_TITLE_PATTERN: (
            game_x,
            game_y,
            max(1, game_width - 1),
            max(1, game_height - 1),
        ),
        HDT_MAIN_TITLE_PATTERN: (
            game_x + main_offset_x,
            game_y + main_offset_y,
            main_width,
            main_height,
        ),
    }

    for title_pattern, target in targets.items():
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
            if all(
                isinstance(value, int)
                and abs(value - expected) <= tolerance
                for value, expected, tolerance in zip(
                    current, target, (1, 1, 2, 2), strict=True
                )
            ):
                continue
            # Do not use --sync here: a compositor fullscreen state can defer
            # the X11 configure request and make xdotool wait indefinitely.
            run("xdotool", "windowsize", window_id, str(target_width), str(target_height))
            run("xdotool", "windowmove", window_id, str(target_x), str(target_y))


def x11_window_is_viewable(window_id: str) -> bool:
    state = run("xwininfo", "-id", window_id)
    return state.returncode == 0 and "Map State: IsViewable" in state.stdout


def load_hidden_x11_state() -> None:
    global _hidden_workspace_x11_windows
    try:
        data = json.loads(HIDDEN_X11_STATE_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return
    if not isinstance(data, dict):
        return
    _hidden_workspace_x11_windows = {
        window_id: identity
        for window_id, identity in data.items()
        if isinstance(window_id, str) and isinstance(identity, dict)
    }


def save_hidden_x11_state() -> None:
    try:
        temporary = HIDDEN_X11_STATE_PATH.with_suffix(".tmp")
        temporary.write_text(
            json.dumps(_hidden_workspace_x11_windows, sort_keys=True),
            encoding="utf-8",
        )
        temporary.replace(HIDDEN_X11_STATE_PATH)
    except OSError:
        pass


def x11_window_identity_matches(
    window_id: str, identity: dict[str, object]
) -> bool:
    pid = run("xdotool", "getwindowpid", window_id)
    title = run("xdotool", "getwindowname", window_id)
    window_class = run("xdotool", "getwindowclassname", window_id)
    return (
        pid.returncode == 0
        and pid.stdout.strip() == str(identity.get("pid"))
        and title.returncode == 0
        and title.stdout.rstrip("\n") == identity.get("title")
        and window_class.returncode == 0
        and window_class.stdout.strip() == identity.get("class")
    )


def find_x11_window_for_client(
    client: dict[str, object], monitor_scale: float
) -> tuple[str, dict[str, object]] | None:
    """Match one Hyprland XWayland client to its X11 window by identity/size."""
    pid = client.get("pid")
    title = client.get("title")
    window_class = client.get("class")
    size = client.get("size")
    if (
        not isinstance(pid, int)
        or not isinstance(title, str)
        or not isinstance(window_class, str)
        or not isinstance(size, list)
        or len(size) != 2
        or not all(isinstance(value, int) for value in size)
    ):
        return None

    expected_width = round(size[0] * monitor_scale)
    expected_height = round(size[1] * monitor_scale)
    result = run("xdotool", "search", "--pid", str(pid))
    if result.returncode != 0:
        return None

    candidates: list[tuple[int, str]] = []
    for window_id in result.stdout.split():
        current_title = run("xdotool", "getwindowname", window_id)
        current_class = run("xdotool", "getwindowclassname", window_id)
        if (
            current_title.returncode != 0
            or current_title.stdout.rstrip("\n") != title
            or current_class.returncode != 0
            or current_class.stdout.strip() != window_class
        ):
            continue
        geometry = run("xdotool", "getwindowgeometry", "--shell", window_id)
        if geometry.returncode != 0:
            continue
        values = parse_shell_geometry(geometry.stdout)
        width = values.get("WIDTH")
        height = values.get("HEIGHT")
        if not isinstance(width, int) or not isinstance(height, int):
            continue
        width_delta = abs(width - expected_width)
        height_delta = abs(height - expected_height)
        if width_delta <= 4 and height_delta <= 4:
            candidates.append((width_delta + height_delta, window_id))

    if not candidates:
        return None
    window_id = min(candidates)[1]
    return window_id, {"pid": pid, "title": title, "class": window_class}


def restore_hidden_x11_windows() -> None:
    for window_id, identity in _hidden_workspace_x11_windows.items():
        if x11_window_identity_matches(window_id, identity):
            run("xdotool", "windowmap", window_id)
    _hidden_workspace_x11_windows.clear()
    save_hidden_x11_state()


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


def client_workspace_is_active(
    client: dict[str, object], monitors: list[object]
) -> bool:
    """Return whether the client's workspace is shown on its assigned monitor."""
    client_monitor = client.get("monitor")
    workspace = client_workspace(client)
    if not isinstance(client_monitor, int) or workspace is None:
        return False

    for monitor in monitors:
        if not isinstance(monitor, dict) or monitor.get("id") != client_monitor:
            continue
        active_workspace = monitor.get("activeWorkspace")
        return (
            isinstance(active_workspace, dict)
            and active_workspace.get("name") == workspace
        )
    return False


def sync_game_workspace_x11_mapping(clients: list[object]) -> None:
    """Hide off-workspace XWayland windows while the game workspace is visible.

    XWayland keeps windows on inactive Hyprland workspaces mapped at the same
    root coordinates. When HearthstoneOverlay enables click-through, the
    otherwise hidden window can therefore receive the click before Hearthstone.
    Unmapping every off-workspace XWayland client on the same monitor removes
    those windows from X11 hit-testing without stopping their applications.
    """
    game = next(
        (
            client
            for client in clients
            if isinstance(client, dict)
            and client.get("mapped", True)
            and client.get("title") == "Hearthstone"
        ),
        None,
    )
    if game is None:
        restore_hidden_x11_windows()
        return

    monitors = read_json("hyprctl", "monitors", "-j")
    if not isinstance(monitors, list):
        return
    if not client_workspace_is_active(game, monitors):
        restore_hidden_x11_windows()
        return

    game_monitor = game.get("monitor")
    game_workspace = client_workspace(game)
    monitor_scale = next(
        (
            monitor.get("scale")
            for monitor in monitors
            if isinstance(monitor, dict) and monitor.get("id") == game_monitor
        ),
        None,
    )
    if (
        not isinstance(game_monitor, int)
        or game_workspace is None
        or not isinstance(monitor_scale, (int, float))
    ):
        return

    changed = False
    for client in clients:
        if (
            not isinstance(client, dict)
            or not client.get("mapped", True)
            or not client.get("xwayland")
            or client.get("monitor") != game_monitor
            or client_workspace(client) == game_workspace
        ):
            continue
        match = find_x11_window_for_client(client, float(monitor_scale))
        if match is None:
            continue
        window_id, identity = match
        if window_id in _hidden_workspace_x11_windows:
            continue
        run("xdotool", "windowunmap", window_id)
        if not x11_window_is_viewable(window_id):
            _hidden_workspace_x11_windows[window_id] = identity
            changed = True
    if changed:
        save_hidden_x11_state()


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
        self.hdt_seen_during_game = False
        self.hdt_missing_since: float | None = None
        self.recovery_requested = False

    def reset(self) -> None:
        self.game_seen = False
        self.missing_since = None
        self.close_requested_at = None
        self.force_sent = False
        self.hdt_seen_during_game = False
        self.hdt_missing_since = None
        self.recovery_requested = False

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
            if hdt_running:
                if self.hdt_missing_since is not None:
                    log_autoclose("HDT recovered while Hearthstone is still running")
                self.hdt_seen_during_game = True
                self.hdt_missing_since = None
                self.recovery_requested = False
            elif self.hdt_seen_during_game:
                if self.hdt_missing_since is None:
                    self.hdt_missing_since = timestamp
                    log_autoclose(
                        "HDT disappeared during Hearthstone; recovery grace period started"
                    )
                elif (
                    not self.recovery_requested
                    and timestamp - self.hdt_missing_since >= HDT_RECOVERY_DELAY_SECONDS
                ):
                    self.recovery_requested = True
                    log_autoclose("Requesting HDT recovery while Hearthstone stays running")
                    return "restart"
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


def request_hdt_recovery() -> None:
    if not HDT_RESTART.is_file():
        log_autoclose(f"HDT recovery launcher is missing: {HDT_RESTART}")
        return
    try:
        subprocess.Popen(
            [str(HDT_RESTART)],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
    except OSError as error:
        log_autoclose(f"Could not start HDT recovery: {error}")


def manage_hdt_autoclose(clients: list[object], state: HdtAutoCloser) -> None:
    # XWayland can retain a dead Wine window. Process state is the reliable
    # lifecycle signal and avoids keeping HDT alive for a zombie Hearthstone.
    game_pids = exact_executable_pids(HEARTHSTONE_PROCESS)
    hdt_pids = exact_executable_pids(HDT_PROCESS)
    action = state.observe(bool(game_pids), bool(hdt_pids))
    if action == "close":
        request_clean_hdt_shutdown()
    elif action == "restart":
        request_hdt_recovery()
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
    load_hidden_x11_state()

    try:
        while _running:
            update_windows()
            hide_empty_wine_helpers()
            hide_overlay_from_taskbar()
            enforce_overlay_no_input_hint()
            clients = normalize_hypr_windows()
            sync_game_workspace_x11_mapping(clients)
            enforce_x11_geometry()
            manage_hdt_autoclose(clients, hdt_auto_closer)
            time.sleep(POLL_SECONDS)
    finally:
        restore_hidden_x11_windows()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
