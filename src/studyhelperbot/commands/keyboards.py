from math import ceil

from aiogram import types

n_days_values = [1, 2, 3, 7, 14, 30]
localizations = {
    "all_courses": {"pl": "Wszystkie przedmioty",
                    "en": "All courses"},
    "to_the_end": {"pl": "Do końca semestru",
                   "en": "Until the end of the semester"}
}


def get_column_keyboard(values_dict, callback_name, callback_key, n_cols=1):
    # TODO: if n_cols is still == 1 and it is the best option -> rewrite
    #  this function, since it can be implemented much much easily
    keyboard = types.InlineKeyboardMarkup(row_width=n_cols)

    n_rows = ceil(len(values_dict) / n_cols)
    for row_id in range(n_rows):
        start = row_id * n_cols
        stop = (row_id + 1) * n_cols
        stop = len(values_dict) if stop > len(values_dict) else stop
        keys, values = list(values_dict), list(values_dict.values())
        for key, value in zip(keys[start:stop], values[start:stop]):
            callback_new_value = {callback_key: key}
            keyboard.insert(types.InlineKeyboardButton(
                text=value,
                callback_data=callback_name.new(**callback_new_value)
            ))
        keyboard.row()
    return keyboard


def get_courses_keyboard(courses, course_ids, callback_data,
                         all_courses_button=True, n_cols=2):
    keyboard = types.InlineKeyboardMarkup(row_width=n_cols)

    if all_courses_button:
        # Add "ALL" button at the first row
        keyboard.insert(types.InlineKeyboardButton(
            text=localizations["all_courses"]["pl"],
            callback_data=callback_data.new(course_id="NULL")
        ))
        keyboard.row()

    n_rows = ceil(len(courses) / n_cols)
    for row_id in range(n_rows):
        start = row_id * n_cols
        stop = (row_id + 1) * n_cols
        stop = len(courses) if stop > len(courses) else stop
        for course_id, course in zip(course_ids[start:stop],
                                     courses[start:stop]):
            keyboard.insert(types.InlineKeyboardButton(
                text=str(course),
                callback_data=callback_data.new(course_id=course_id)
            ))
        keyboard.row()
    return keyboard


def get_days_keyboard(callback_data, n_cols=2):
    keyboard = types.InlineKeyboardMarkup(row_width=n_cols)

    # Add "ALL" button at the first row
    keyboard.insert(types.InlineKeyboardButton(
        text=localizations["to_the_end"]["pl"],
        callback_data=callback_data.new(n_days="NULL")
    ))
    keyboard.row()

    n_rows = ceil(len(n_days_values) / n_cols)
    for row_id in range(n_rows):
        start = row_id * n_cols
        stop = (row_id + 1) * n_cols
        stop = len(n_days_values) if stop > len(n_days_values) else stop
        for n_days in n_days_values[start:stop]:
            keyboard.insert(types.InlineKeyboardButton(
                text=str(n_days),
                callback_data=callback_data.new(n_days=n_days)
            ))
        keyboard.row()
    return keyboard
