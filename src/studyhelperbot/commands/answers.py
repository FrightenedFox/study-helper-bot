from pandas import DataFrame


# --------------------- #
# Help and info answers #
# --------------------- #


def start(lang="pl"):
    # TODO: finish, correct and improve every answer
    if lang == "pl":
        return ("Witam! Jestem botem drugiego roku "
                "Inżynierii i Analizy Danych na PRz! "
                "Żeby dowiedzieć się więcej o moich możliwościach, "
                "wpisz (lub kliknij) /help.\n\n"
                "Żeby zarejestrować się wpisz /register.")


def successful_verification(lang="pl"):
    # TODO: since we already know users' name, it would
    #  be nice to use it as well
    #  (e.g. Dear, Aurthur, verification passed successfully!)
    if lang == "pl":
        return "Udało się zalogować!"


# --------------- #
# Warning answers #
# --------------- #


def unknown_command(lang="pl"):
    if lang == "pl":
        return "Nie znam takiego polecenia :o"


def empty_query(try_again=False, lang="pl"):
    ans = "Nie udało się znaleźć zajęć w tym terminie :p"
    if try_again:
        ans += ("\nMożesz spróbować wpisać datę ponownie. Jeżeli nie chcesz"
                "kontynuować możesz kliknąć /cancel..")
    if lang == "pl":
        return ans


def permission_conflict(lang="pl"):
    if lang == "pl":
        return "Niestety, nie masz uprawnień do tego polecenia! :p"


def you_are_already_registered(lang="pl"):
    if lang == "pl":
        return ("Już jesteś zarejstrowany, "
                "niema potrzeby robić to ponownie.")


# ------------- #
# Error answers #
# ------------- #


def incorrect_date(lang="pl"):
    if lang == "pl":
        return ("Podana wartość nie odpowiada formatowi daty dd.mm.rrrr, "
                "spróbuj ponownie wpisać datę. \n\n"
                "Możesz również wyjść z aktualnej procedury "
                "wpisując /cancel.")


def incorrect_time(lang="pl"):
    if lang == "pl":
        return ("Podana wartość nie odpowiada formatowi czasu gg.mm,"
                "spróbuj ponownie wpisać czas. \n\n"
                "Możesz równierż wyjść z aktualnej procedury "
                "wpisując /cancel.")


def incorrect_verification_code(lang="pl"):
    if lang == "pl":
        return ("Podany kod jest niepoprawny! \n"
                "Żeby spróbować ponownie wpisz polecnie jeszcze raz.")


def obligatory_input(lang="pl"):
    if lang == "pl":
        return ("Nie można pominąć tej wartości! "
                "Proszę wpisać podać poprawną wartość. \n\n"
                "Możesz równierż wyjść z aktualnej procedury "
                "wpisując /cancel.")


# -------------- #
# Prompt answers #
# -------------- #


def register(url, lang="pl"):
    if lang == "pl":
        return (f"Dostęp do tego botu mają ponad 500 000 000 osób, "
                f"więc nie mogę dopuszczać każdego -_-.\n"
                f"Za chwilę wyślę do ciebie linka, za pomocą którego"
                f" będziesz mógł (mogła) się zalogować, i podać mi "
                f"6-znakowy kod weryfikacji.\n\n"
                f"Taka działanosćś pozwoli mi dowiedzieć się czy "
                f"naprawdę jesteś studentem (studentką), "
                f"na którym roku studiujesz oraz pobrać twój rozkład zajęć."
                f"\n\n{url}")


def wait_for_link(url, lang="pl"):
    if lang == "pl":
        return (f"Za chwilę wyślę do ciebie linka, za pomocą którego"
                f" będziesz mógł (mogła) się zalogować, i podać mi "
                f"6-znakowy kod weryfikacji."
                f"\n\n{url}")


def choose_request(ending, lang="pl"):
    endings = {
        "day": {"pl": "ilość dni"},
        "course": {"pl": "przedmiot"},
        "action": {"pl": "akcję"},
        "activity:hw_done_by_activity": {
            "pl": "zajęcie, do którego trzeba oddać zadanie domowe"
        }
    }
    if lang == "pl":
        return f"Proszę wybrać {endings[ending][lang]}:"


def choose_from_results(course, date, lang="pl"):
    if lang == "pl":
        return (f"Wybrany przedmiot: \n\t*{course}*\n"
                f"wybrany dzień: \n\t*{date}*\n"
                f"Znalezione zajęcia:")


def enter_request(ending, skip=False, lang="pl"):
    endings = {
        "date": {"pl": "datę (używając formatu dd.mm.yyyy)"},
        "time": {"pl": "czas (używając formatu hh:mm)"},
        "activity:topics_discussed": {
            "pl": "nazwy tematów, omówionych na zajęciu"
        },
        "activity:lecture_description": {
            "pl": "dokładny opis zajęcia"
        },
        "activity:hw_short_description": {
            "pl": "sktórcony opis zadania domowego"
        },
        "activity:hw_full_description": {
            "pl": "dokładny opis zadania domowego"
        },
        "activity:hw_turn_in_method": {
            "pl": "sposób oddania zadania domowego"
        },
        "activity:hw_due_date": {
            "pl": "termin końcowy oddania zadania domowego"
        },
        "activity:attached_files": {
            "pl": "załącznik"
        },
        "activity:other_details": {
            "pl": "dodatkowe informacje"
        },
    }
    if skip:
        skip_text = {"pl": ".\n\nTen punkt nie jest obowiązkowym, "
                           "żeby go pominąć proszę wpisać polecenie"
                           " /skip"}[lang]
    else:
        skip_text = ":"
    if lang == "pl":
        return f"Prosze podać {endings[ending][lang]}{skip_text}"


# ------------- #
# Print answers #
# ------------- #


def storytellers_overview(activities: DataFrame, lang="pl"):
    # TODO: add user preferences and modes
    #  consider rendering and showing an image
    result = ""
    if activities.shape[0] == 0:
        result = empty_query(lang=lang)
    elif activities.shape[0] <= 10:
        result += "```"
        last_date = None
        for ind, act in activities.iterrows():
            if last_date != act.start_time.date():
                last_date = act.start_time.date()
                result += f"\n{last_date.strftime(' %a %d %B %Y '):=^35}\n"
            result += f"{act.course_name:.<24.22}"
            result += f"{act.start_time.time().strftime('%H:%M-')}"
            result += f"{act.end_time.time().strftime('%H:%M')}\n"
            result += f"{act.group_type:>7.3} {act.group_number:<3}"
            result += f"{act.room:<25.15}\n"
        result += "```"
    else:
        result = "Too many results (>10). Not implemented yet, coming soon..."
    result = result.replace(".", "\\.").replace("=", "\\=").replace("-", "\\-")
    result = result.replace("(", "\\(").replace(")", "\\)").replace(">", "\\>")
    if lang == "pl":
        return result
