from residences.models import City, Residence

RESIDENCE_TYPE_BY_TEXT: dict[str, Residence.Type] = {
    'vrijstaand huis': Residence.Type.HOUSE_DETACHED,
    'vrijstaande woning': Residence.Type.HOUSE_DETACHED,

    'twee-onder-een-kap': Residence.Type.HOUSE_SEMI_DETACHED,
    'twee-onder-één-kap': Residence.Type.HOUSE_SEMI_DETACHED,

    'duplex': Residence.Type.HOUSE_DUPLEX,

    'hoekwoning': Residence.Type.HOUSE_TERRACED,
    'rijtjeshuis': Residence.Type.HOUSE_TERRACED,
    'tussenwoning': Residence.Type.HOUSE_TERRACED,

    'eengezinswoning': Residence.Type.HOUSE_UNKNOWN,
    'gezinswoning': Residence.Type.HOUSE_UNKNOWN,

    'appartement': Residence.Type.APARTMENT,
    'flat': Residence.Type.APARTMENT,
    'galerijflat': Residence.Type.APARTMENT,

    'maisonette': Residence.Type.MAISONNETTE
}


def lookup_city(name: str) -> City:
    return City.objects.get(name=name)


def lookup_residence_type(name: str, alternative_name: str) -> Residence.Type:
    result = RESIDENCE_TYPE_BY_TEXT.get(name.lower(), Residence.Type.UNKNOWN)
    if result in [Residence.Type.HOUSE_UNKNOWN, Residence.Type.UNKNOWN]:
        alternative_result = RESIDENCE_TYPE_BY_TEXT.get(alternative_name.lower(), Residence.Type.UNKNOWN)
        if alternative_result != Residence.Type.UNKNOWN:
            return alternative_result
    return result


def is_existing_residence(**kwargs):
    return Residence.objects.filter(**kwargs).count() > 0
