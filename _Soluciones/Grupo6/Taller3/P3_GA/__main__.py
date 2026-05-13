import sys


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode == "gui":
        from .GUI.app import main as gui_main
        gui_main()
    elif mode == "console":
        from .console.app import main as console_main
        console_main()
    else:
        print("Usage: python -m Taller3.P3_GA [console|gui]")
        print()
        choice = input("Launch (1) Console  or  (2) GUI ? ").strip()
        if choice == "2":
            from .GUI.app import main as gui_main
            gui_main()
        else:
            from .console.app import main as console_main
            console_main()


if __name__ == "__main__":
    main()
