"""scavenger hunt game where printed barcodes are linked to questions from a grok API call and are integrated into a CLI game"""

from datetime import datetime, date



class Player:
        
    def __init__(self, name: str, dob: date) -> None:

        today = date.today()
        total_months = ((today.year - dob.year) * 12) + (today.month - dob.month)
        years_old = total_months//12
        months_old = total_months%12

        self.name = name
        self.age = f"{years_old} years, {months_old} month(s)"


def main():
    p1 = Player("Blanton", date(1996, 8, 1))
    print(p1.name, p1.age)


if __name__ == "__main__":
    main()