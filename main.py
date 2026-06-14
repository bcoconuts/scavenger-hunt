"""scavenger hunt game where printed barcodes are linked to questions from a grok API call and are integrated into a CLI game"""

import storage
import sys
import workflows
from ui_protocol import UI


def main():
    """Program entry point: pick the UI, load the session, run the menu loop."""
    ui : UI
    if "--gui" in sys.argv:
        import gui
        ui = gui.UIDisplay()
    else:
        import cli as ui
    ui.greet_user()
    session = storage.load_session()
    workflows.route_menu_actions(session, ui)

if __name__ == "__main__":
    main()