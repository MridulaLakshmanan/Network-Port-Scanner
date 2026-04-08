"""Network Port Scanner

Main entry point for the application.

This launcher chooses the GUI when supported, otherwise falls back to a
command-line runner. The GUI (CustomTkinter) may abort on older macOS
versions; therefore we check the OS version and run a safe CLI fallback
when necessary.
"""

import sys
import platform

def _macos_supports_gui() -> bool:
    """Return True when macOS version is new enough for the GUI.

    CustomTkinter (and some Tk integrations) can require macOS 14+.
    We detect the macOS version and avoid creating the GUI on older
    systems to prevent a hard abort.
    """
    if sys.platform != "darwin":
        return True
    try:
        ver = platform.mac_ver()[0]
        if not ver:
            return False
        major = int(ver.split(".")[0])
        return major >= 14
    except Exception:
        return False


def main():
    # Prefer the custom GUI when the platform supports it. Otherwise try a
    # plain Tkinter GUI (no third-party library) and finally fall back to CLI.
    if _macos_supports_gui():
        try:
            from ui import main as gui_main
            gui_main()
            return
        except Exception as e:
            print("Custom GUI unavailable or failed; falling back to Tkinter GUI or CLI.\n", e)

    # Try standard tkinter-based GUI (safer on older macOS)
    try:
        from tk_ui import main as tk_main
        tk_main()
        return
    except Exception as e:
        print("Tkinter GUI unavailable or failed; falling back to CLI.\n", e)

    # Final fallback: CLI runner
    from cli import main as cli_main
    cli_main()


if __name__ == "__main__":
    main()
