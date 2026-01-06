import os
import sys


def main():
    # Handle both development and PyInstaller environments
    if getattr(sys, 'frozen', False):
        # Running in a PyInstaller bundle
        # The src modules are already available in the bundled path
        pass
    else:
        # Running in development mode
        repo_root = os.path.dirname(os.path.abspath(__file__))
        src_path = os.path.join(repo_root, 'src')
        if src_path not in sys.path:
            sys.path.insert(0, src_path)

    from pomocus import main as pomocus_main

    pomocus_main()


if __name__ == "__main__":
    main()
