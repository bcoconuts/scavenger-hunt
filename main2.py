"""scavenger hunt game where printed barcodes are linked to questions from a grok API call and are integrated into a CLI game"""

import storage

def main():
    session = storage.load_session()
    session.greet_user()
    session.route_menu_actions()


if __name__ == "__main__":
    main()