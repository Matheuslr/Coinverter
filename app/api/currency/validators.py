def iso_4217_check(iso_4217: str):
    if iso_4217 and not iso_4217.isalpha():
        raise ValueError("iso_4217 must contain only characters.")
    if len(iso_4217) != 3:
        raise ValueError("iso_4217 must contain only 3 characters.")
    return str(iso_4217).upper()
