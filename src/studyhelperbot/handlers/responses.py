def template(lang="pl"):
    # ODO: finish
    if lang == "pl":
        return ("Your"
                "message")


def start(lang="pl"):
    if lang == "pl":
        return ("Witam! Jestem botem drugiego roku "
                "Inżynierii i Analizy Danych na PRz! "
                "Żeby dowiedzieć się więcej o moich możliwościach, "
                "wpisz (lub kliknij) /help.\n\n"
                "Żeby zarejstrować się wpisz /register.")


def register(lang="pl"):
    if lang == "pl":
        return ("Dostęp do tego botu mają ponad 500 000 000 osób, "
                "więc nie mogę dopuszczać każdego -_-.\n"
                "Za chwilę wyślę do ciebie linka, za pomocą którego"
                " będziesz mógł (mogła) się zalogować, i podać mi "
                "6-znakowy kod weryfikacji.\n\n"
                "Taka działanosćś pozwoli mi dowiedzieć się czy "
                "naprawdę jesteś studentem, na którym roku studiujesz "
                "oraz pobrać twój rozkład zajęć.")


def you_are_already_registered(lang="pl"):
    # TODO: finish
    if lang == "pl":
        return ("Już jesteś zarejstrowany, "
                "niema potrzeby robić to ponownie.")


def wait_for_link(lang="pl"):
    # TODO: finish
    if lang == "pl":
        return ("Za chwilę wyślę do ciebie linka, za pomocą którego"
                " będziesz mógł (mogła) się zalogować, i podać mi "
                "6-znakowy kod weryfikacji")


def incorrect_verification_code(lang="pl"):
    # TODO: finish
    if lang == "pl":
        return "Podany kod jest niepoprawny!"


def successful_verification(lang="pl"):
    # TODO: finish + since we already know users' name, it would
    #  be nice to use it as well
    #  (e.g. Dear, Aurthur, verification passed successfully!)
    if lang == "pl":
        return "Udało się zalogować!"


def unknown_command(lang="pl"):
    # TODO: finish
    if lang == "pl":
        return "Sorki, ale nie wiem co ci odpisać :o"


def permission_conflict(lang="pl"):
    # TODO: finish
    if lang == "pl":
        return "Niestety, nie masz uprawnień do tego polecenia! :p"
