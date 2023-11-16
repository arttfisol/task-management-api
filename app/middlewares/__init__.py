from datetime import datetime


def is_valid_date(date_string):
    try:
        datetime.strptime(date_string, "%Y-%m-%d")
        return True
    except Exception:
        return False


def validate_query_type(value, _type, enum):
    # don't need to check str type for query string
    if _type == "int" and not value.isdigit():
        return False
    elif _type == "date" and not is_valid_date(value):
        return False

    if enum and value not in enum:
        return False

    return True


def validate_query(query, field, inner_type, required, is_array, enum):
    value = query.get(field)

    if value is None and required:
        raise ValueError(f"{field} is required")

    if field in query:
        if is_array:
            value = value.split(",")
            if len(set(value)) != len(value):
                verb = "have" if is_array else "has"
                raise ValueError(f"{field} {verb} duplicate value")
        else:
            value = [value]

        for v in value:
            if not validate_query_type(v, inner_type, enum):
                verb = "are" if is_array else "is"
                raise ValueError(f"{field} {verb} invalid")

    return


def validate_body_type(value, _type, enum):
    if _type == "date":
        if type(value) is not str or not is_valid_date(value):
            return False
    elif type(value) is not _type:
        return False

    if enum and value not in enum:
        return False

    return True


def validate_body(body, field, inner_type, required, enum):
    value = body.get(field)

    if value is None and required:
        raise ValueError(f"{field} is required")

    if field in body and not validate_body_type(value, inner_type, enum):
        raise ValueError(f"{field} is invalid")

    return
