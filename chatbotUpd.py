import pickle
from collections import UserDict
from datetime import date, datetime, timedelta


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    pass


class Phone(Field):
    def __init__(self, value):
        if not isinstance(value, str) or len(value) != 10 or not value.isdigit():
            raise ValueError("Phone number must contain exactly 10 digits.")
        super().__init__(value)


class Birthday(Field):
    def __init__(self, value):
        try:
            date_obj = datetime.strptime(value, "%d.%m.%Y").date()
            super().__init__(date_obj)
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        phone_obj = self.find_phone(phone)
        if not phone_obj:
            raise ValueError("Phone number not found.")
        self.phones.remove(phone_obj)

    def edit_phone(self, old_phone, new_phone):
        phone_obj = self.find_phone(old_phone)
        if not phone_obj:
            raise ValueError("Phone number not found.")
        index = self.phones.index(phone_obj)
        self.phones[index] = Phone(new_phone)

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}, birthday: {self.birthday.value if self.birthday else 'Not specified'}"


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def get_upcoming_birthdays(self):
        upcoming_birthdays = []
        today = date.today()

        for record in self.data.values():
            if record.birthday is None:
                continue

            bday = record.birthday.value
            bday_this_year = bday.replace(year=today.year)

            if bday_this_year < today:
                bday_this_year = bday_this_year.replace(year=today.year + 1)

            days_diff = (bday_this_year - today).days

            if 0 <= days_diff <= 7:
                congratulation_date = bday_this_year
                if congratulation_date.weekday() == 5:  # Суббота
                    congratulation_date += timedelta(days=2)
                elif congratulation_date.weekday() == 6:  # Воскресенье
                    congratulation_date += timedelta(days=1)

                upcoming_birthdays.append(
                    {
                        "name": record.name.value,
                        "congratulation_date": congratulation_date.strftime("%d.%m.%Y"),
                    }
                )
        return upcoming_birthdays


def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (KeyError, ValueError, IndexError) as e:
            return str(e) or "Give me correct arguments please."

    return inner


@input_error
def add_contact(args, book):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        is_new = True
    else:
        is_new = False

    if phone:
        record.add_phone(phone)

    if is_new:
        book.add_record(record)

    return message


@input_error
def change_phone(args, book):
    name, old_phone, new_phone, *_ = args
    record = book.find(name)
    if record is None:
        raise ValueError(f"Contact {name} not found.")
    record.edit_phone(old_phone, new_phone)
    return f"Phone updated for {name}."


@input_error
def show_phone(args, book):
    (name,) = args
    record = book.find(name)
    if record is None:
        raise ValueError(f"Contact {name} not found.")
    return "; ".join(p.value for p in record.phones)


@input_error
def show_all(book):
    if not book.data:
        return "Address book is empty."
    return "\n".join(str(record) for record in book.data.values())


@input_error
def add_birthday(args, book):
    name, birthday_str, *_ = args
    record = book.find(name)
    if record is None:
        raise ValueError(f"Contact {name} not found.")
    record.add_birthday(birthday_str)
    return f"Birthday added for {name}."


@input_error
def show_birthday(args, book):
    (name,) = args
    record = book.find(name)
    if record is None:
        raise ValueError(f"Contact {name} not found.")
    if record.birthday is None:
        return f"Birthday for {name} is not set."
    return f"Birthday for {name}: {record.birthday.value.strftime('%d.%m.%Y')}"


@input_error
def birthdays(args, book):
    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        return "No birthdays in the next week."

    result = []
    for item in upcoming:
        result.append(f"{item['name']}: {item['congratulation_date']}")
    return "\n".join(result)


def parse_input(user_input):
    cmd, *args = user_input.strip().split()
    cmd = cmd.lower()
    return cmd, args


def save_data(book, filename="address_book.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)


def load_data(filename="address_book.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()


def main():
    book = load_data()
    print("Welcome to the assistant bot!")

    while True:
        user_input = input("Enter a command: ")
        if not user_input.strip():
            continue

        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            save_data(book)
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_phone(args, book))

        elif command == "phone":
            print(show_phone(args, book))

        elif command == "all":
            print(show_all(book))

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(args, book))

        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()
