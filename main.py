"""scavenger hunt game where printed barcodes are linked to questions from a grok API call and are integrated into a CLI game"""

import storage
import sys
import workflows


def main():
    """Program entry point: pick the UI, load the session, run the menu loop."""
    if "--gui" in sys.argv:
        import cli as ui #TODO - change cli to gui once gui.py exists
    else:
        import cli as ui
    session = storage.load_session()
    workflows.route_menu_actions(session, ui)

if __name__ == "__main__":
    main()