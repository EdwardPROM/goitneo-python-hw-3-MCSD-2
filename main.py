from collections import defaultdict, UserDict
from datetime import datetime, timedelta


class Field:

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):

    def __init__(self, value):
        if not value:
            raise ValueError("Name cannot be empty")
        super().__init__(value)


class Phone(Field):

    def __init__(self, value):
        if not self.validate_phone(value):
            raise ValueError("Invalid phone number format")
        super().__init__(value)

    @staticmethod
    def validate_phone(value):
        return len(value) == 10 and value.isdigit()


class Birthday(Field):

    def __init__(self, value):
        if not self.validate_birthday(value):
            raise ValueError("Invalid birthday format. Use DD.MM.YYYY")
        super().__init__(value)

    @staticmethod
    def validate_birthday(value):
        try:
            datetime.strptime(value, '%d.%m.%Y')
            return True
        except ValueError:
            return False

    def to_datetime(self):
        return datetime.strptime(self.value, '%d.%m.%Y')


class Record:

    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if p.value != phone]

    def remove_phones(self):
        self.phones = []

    def edit_phone(self, old_phone, new_phone):
        for phone in self.phones:
            if phone.value == old_phone:
                phone.value = new_phone
                break

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    def get_birthday(self):
    
        return self.birthday

    def __str__(self):
        phones_str = "; ".join(str(phone) for phone in self.phones)
        return f"Contact name: {self.name}, phones: {phones_str}"


class AddressBook(UserDict):

    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name) -> Record:
        return self.data.get(name, None)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def get_birthdays_per_week(self):
        birthdays_by_day = defaultdict(list)

        today = datetime.today().date()

        for name in self.data:
            birthday = self.data[name].get_birthday()

            if not birthday:
                continue

            birthday = birthday.to_datetime().date()

            birthday_this_year = birthday.replace(year=today.year)

            if birthday_this_year < today:
                birthday_this_year = birthday_this_year.replace(
                    year=today.year + 1)

            if birthday_this_year.weekday() > 4:
                delta_days = 6 - birthday_this_year.weekday() + 1
                birthday_this_year = birthday_this_year.replace(
                    day=birthday.day + delta_days)

            delta_days = (birthday_this_year - today).days
            if delta_days >= 7:
                continue

            day_of_week = (today + timedelta(days=delta_days)).strftime("%A")

            birthdays_by_day[day_of_week].append(name)

        return birthdays_by_day


def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            return "Give me name and phone please."
        except KeyError as e:
            return f"Contact '{e.args[0]}' not found."
        except IndexError:
            return "Invalid command format."

    return inner


def parse_input(user_input: str):
    try:
        cmd, *args = user_input.split()
        cmd = cmd.strip().lower()
    except ValueError:
        return None, []

    return cmd, *args


@input_error
def add_contact(args, book: AddressBook):
    name, phone = args
    record = Record(name)
    record.add_phone(phone)
    book.add_record(record)
    return "Contact added."


@input_error
def change_contact(args, book: AddressBook):
    name, new_phone = args

    record = book.find(name)

    if record is None:
        raise KeyError(name)

    record.remove_phones()

    record.add_phone(new_phone)
    return "Contact updated."


@input_error
def show_phone(args, book: AddressBook):
    if len(args) != 1:
        raise IndexError()

    name = args[0]

    record = book.find(name)

    if record is None:
        raise KeyError(name)

    return record.phones[0].value


@input_error
def show_all(book: AddressBook):
    if not book:
        return "No contacts found."

    return "\n".join([f"{name}: {record.phones[0].value}"
                      for name, record in book.items()])


@input_error
def add_birthday(args, book: AddressBook):
    name, birthday = args

    record = book.find(name)

    if record is None:
        raise KeyError(name)

    record.add_birthday(birthday)
    return "Birthday added."


@input_error
def show_birthday(args, book: AddressBook):
    if len(args) != 1:
        raise IndexError()

    name = args[0]

    record = book.find(name)

    if record is None:
        raise KeyError(name)

    birthday = record.get_birthday()

    if birthday is None:
        return "Birthday is not set."

    return record.birthday.value


@input_error
def birthdays(book: AddressBook):
    bdays = book.get_birthdays_per_week()

    if not bdays:
        print("No birthdays in the next week.")
        return

    print("Birthdays in the next week:")
    for day, name in bdays.items():
        print(f"{day}: {name}")


def main():
    book = AddressBook()

    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "all":
            print(show_all(book))
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            birthdays(book)
        elif command == "hello":
            print("How can I help you?")
        elif command in ["close", "exit"]:
            print("Good bye!")
            break
        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()