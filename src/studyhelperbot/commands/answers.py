def start(lang="pl"):
    # TODO: finish, correct and improve every answer
    if lang == "pl":
        return ("Witam! Jestem botem drugiego roku "
                "Inżynierii i Analizy Danych na PRz! "
                "Żeby dowiedzieć się więcej o moich możliwościach, "
                "wpisz (lub kliknij) /help.\n\n"
                "Żeby zarejestrować się wpisz /register.")


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


def you_are_already_registered(lang="pl"):
    if lang == "pl":
        return ("Już jesteś zarejstrowany, "
                "niema potrzeby robić to ponownie.")


def wait_for_link(url, lang="pl"):
    if lang == "pl":
        return (f"Za chwilę wyślę do ciebie linka, za pomocą którego"
                f" będziesz mógł (mogła) się zalogować, i podać mi "
                f"6-znakowy kod weryfikacji."
                f"\n\n{url}")


def incorrect_verification_code(lang="pl"):
    if lang == "pl":
        return "Podany kod jest niepoprawny!"


def successful_verification(lang="pl"):
    # TODO: since we already know users' name, it would
    #  be nice to use it as well
    #  (e.g. Dear, Aurthur, verification passed successfully!)
    if lang == "pl":
        return "Udało się zalogować!"


def unknown_command(lang="pl"):
    if lang == "pl":
        return "Sorki, ale nie wiem co ci odpisać :o"


def permission_conflict(lang="pl"):
    if lang == "pl":
        return "Niestety, nie masz uprawnień do tego polecenia! :p"


def choose_commits(lang="pl"):
    if lang == "pl":
        return "Prosze wybrać akcję:"


def choose_request(ending, lang="pl"):
    endings = {
        "days": {"pl": "ilość dni"},
        "courses": {"pl": "przedmiot"}
    }
    if lang == "pl":
        return f"Proszę wybrać {endings[ending][lang]}:"


def storytellers_overview(activities, lang="pl"):
    # TODO: add user preferences and modes
    #  consider rendering and showing an image
    result = ""
    if not activities:
        result = "Brak wyników :p"
    elif len(activities) < 10:
        result += "```"
        last_date = None
        for activity in activities:
            if last_date != activity[1].date():
                last_date = activity[1].date()
                result += f"\n{last_date.strftime(' %a %d %B %Y '):=^35}\n"
            result += f"{activity[6]:.<24.22}"
            result += f"{activity[1].time().strftime('%H:%M-')}"
            result += f"{activity[2].time().strftime('%H:%M')}\n"
            result += f"{activity[4]:>7.3} {activity[5]:<3}"
            result += f"{activity[3]:<25.15}\n"
        result += "```"
    else:
        result = "Too many results (>10). Coming soon..."
    result = result.replace(".", "\\.").replace("=", "\\=").replace("-", "\\-")
    result = result.replace("(", "\\(").replace(")", "\\)").replace(">", "\\>")
    if lang == "pl":
        return result
