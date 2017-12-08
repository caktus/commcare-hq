from __future__ import absolute_import

import os

import jsonobject
import phonenumbers
import yaml

from custom.enikshay.case_utils import (
    CASE_TYPE_EPISODE,
    CASE_TYPE_PERSON,
    get_person_locations,
)
from custom.enikshay.const import (
    ENROLLED_IN_PRIVATE,
    PRIVATE_SECTOR,
    PUBLIC_SECTOR,
    SECTORS,
    TREATMENT_SUPPORTER_FIRST_NAME,
    TREATMENT_SUPPORTER_LAST_NAME,
    TREATMENT_SUPPORTER_PHONE,
)
from custom.enikshay.integrations.ninetyninedots.const import (
    MERM_DAILY_REMINDER_STATUS,
    MERM_DAILY_REMINDER_TIME,
    MERM_ID,
    MERM_REFILL_REMINDER_DATE,
    MERM_REFILL_REMINDER_STATUS,
    MERM_REFILL_REMINDER_TIME,
    MERM_RT_HOURS,
    NINETYNINEDOTS_NUMBERS,
)
from dimagi.ext.jsonobject import StrictJsonObject
from dimagi.utils.decorators.memoized import memoized


class DotsApiSectorParam(StrictJsonObject):
    public = jsonobject.StringProperty()
    private = jsonobject.StringProperty()
    both = jsonobject.StringProperty()

    def __init__(self, *args, **kwargs):
        try:
            _obj = args[0]
        except IndexError:
            _obj = {}
        _obj.update(kwargs)

        if _obj:
            if "both" in _obj and ("public" in _obj or "private" in _obj):
                raise ValueError("Can't define 'public' or 'private' options with 'both'")
            if "both" not in _obj and len(set(("public", "private")) - set(_obj.keys())) > 0:
                raise ValueError("Must contain both public and private options")

        return super(DotsApiSectorParam, self).__init__(*args, **kwargs)


class DotsApiParamChoices(DotsApiSectorParam):
    public = jsonobject.ListProperty()
    private = jsonobject.ListProperty()
    both = jsonobject.ListProperty()


class DotsApiParam(StrictJsonObject):
    api_param_name = jsonobject.StringProperty(required=True)
    required_ = jsonobject.BooleanProperty(default=False, name='required')
    choices = jsonobject.ObjectProperty(DotsApiParamChoices)
    case_type = jsonobject.ObjectProperty(DotsApiSectorParam)
    case_property = jsonobject.ObjectProperty(DotsApiSectorParam)

    def get_by_sector(self, prop, sector):
        prop = getattr(self, prop)
        if isinstance(prop, DotsApiSectorParam):
            return getattr(prop, sector) or prop.both
        else:
            return prop


class DotsApiParams(StrictJsonObject):
    api_params = jsonobject.ListProperty(DotsApiParam)

    def params_by_case_type(self, sector, case_type):
        return [param for param in self.api_params
                if param.get_by_sector('case_type', sector) == case_type]


@memoized
def load_api_spec():
    """Loads API spec from api_properties.yaml and validates that the spec is correct
    """
    filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'api_properties.yaml')
    with open(filename, 'r') as f:
        spec = DotsApiParams(yaml.load(f))
    return spec


class MermParams(StrictJsonObject):
    IMEI = jsonobject.StringProperty(required=False, exclude_if_none=True)
    daily_reminder_status = jsonobject.StringProperty(required=False, exclude_if_none=True)
    daily_reminder_time = jsonobject.StringProperty(required=False, exclude_if_none=True)  # HH:mm
    refill_reminder_status = jsonobject.StringProperty(required=False, exclude_if_none=True)
    refill_reminder_datetime = jsonobject.StringProperty(
        required=False,
        exclude_if_none=True
    )  # yy/MM/dd HH:mm:ss
    RT_hours = jsonobject.StringProperty(
        required=False,
        exclude_if_none=True
    )  # 1 = 12 hours; i.e. for 3 days - RT_hours = 6


class BasePatientPayload(StrictJsonObject):
    sector = jsonobject.StringProperty(required=True)
    state_code = jsonobject.StringProperty(required=False)
    district_code = jsonobject.StringProperty(required=False)
    tu_code = jsonobject.StringProperty(required=False)
    phone_numbers = jsonobject.StringProperty(required=False)
    treatment_supporter_name = jsonobject.StringProperty(required=False)
    treatment_supporter_phone_number = jsonobject.StringProperty(required=False)
    merm_params = jsonobject.ObjectProperty(MermParams, exclude_if_none=True)

    @classmethod
    def create(cls, person_case, episode_case):
        payload_kwargs = {
            "sector": cls._sector,
        }
        api_spec = load_api_spec()
        person_properties = api_spec.params_by_case_type(cls._sector, CASE_TYPE_PERSON)
        episode_properties = api_spec.params_by_case_type(cls._sector, CASE_TYPE_EPISODE)

        for episode_property in episode_properties:
            case_property = episode_property.get_by_sector('case_property', cls._sector)
            payload_kwargs[episode_property.api_param_name] = episode_case.get_case_property(case_property)
        for person_property in person_properties:
            case_property = person_property.get_by_sector('case_property', cls._sector)
            payload_kwargs[person_property.api_param_name] = person_case.get_case_property(case_property)

        person_case_properties = person_case.dynamic_case_properties()
        episode_case_properties = episode_case.dynamic_case_properties()
        all_properties = episode_case_properties.copy()
        all_properties.update(person_case_properties)  # items set on person trump items set on episode
        payload_kwargs['phone_numbers'] = _get_phone_numbers(all_properties)
        if episode_case_properties.get(MERM_ID, '') != '':
            payload_kwargs.update(get_merm_params(episode_case_properties))

        payload_kwargs.update(get_treatment_supporter_info(episode_case_properties))
        payload_kwargs.update(cls.get_locations(person_case, episode_case))

        return cls(payload_kwargs)


def get_treatment_supporter_info(episode_case_properties):
    return {
        "treatment_supporter_name": u"{} {}".format(
            episode_case_properties.get(TREATMENT_SUPPORTER_FIRST_NAME, ''),
            episode_case_properties.get(TREATMENT_SUPPORTER_LAST_NAME, ''),
        ),
        "treatment_supporter_phone_number": (
            _format_number(
                _parse_number(episode_case_properties.get(TREATMENT_SUPPORTER_PHONE))
            )
        )
    }


def get_merm_params(episode_case_properties):
    refill_reminder_date = episode_case_properties.get(MERM_REFILL_REMINDER_DATE, None)
    refill_reminder_time = episode_case_properties.get(MERM_REFILL_REMINDER_TIME, None)
    if refill_reminder_time and refill_reminder_date:
        refill_reminder_datetime = "{}T{}".format(refill_reminder_date, refill_reminder_time)
    else:
        refill_reminder_datetime = None

    return {"merm_params": {
        "IMEI": episode_case_properties.get(MERM_ID, None),
        "daily_reminder_status": episode_case_properties.get(MERM_DAILY_REMINDER_STATUS, None),
        "daily_reminder_time": episode_case_properties.get(MERM_DAILY_REMINDER_TIME, None),
        "refill_reminder_status": episode_case_properties.get(MERM_REFILL_REMINDER_STATUS, None),
        "refill_reminder_datetime": refill_reminder_datetime,
        "RT_hours": episode_case_properties.get(MERM_RT_HOURS, None),
    }}



class BasePublicPatientPayload(BasePatientPayload):
    _sector = PUBLIC_SECTOR
    phi_code = jsonobject.StringProperty(required=False, exclude_if_none=True)

    @staticmethod
    def get_locations(person_case, episode_case):
        person_locations = get_person_locations(person_case, episode_case)
        return {
            "state_code": person_locations.sto,
            "district_code": person_locations.dto,
            "tu_code": person_locations.tu,
            "phi_code": person_locations.phi,
        }


class BasePrivatePatientPayload(BasePatientPayload):
    _sector = PRIVATE_SECTOR
    he_code = jsonobject.StringProperty(required=False, exclude_if_none=True)

    @staticmethod
    def get_locations(person_case, episode_case):
        person_locations = get_person_locations(person_case, episode_case)
        return {
            "state_code": person_locations.sto,
            "district_code": person_locations.dto,
            "tu_code": person_locations.tu,
            "he_code": person_locations.pcp,
        }


def get_payload_properties(sector):
    if sector not in SECTORS:
        raise ValueError('sector argument should be one of {}'.format(",".join(SECTORS)))

    properties = {}
    spec = load_api_spec()
    for param in spec.api_params:
        properties[param.api_param_name] = jsonobject.StringProperty(
            choices=param.get_by_sector('choices', sector),
            required=param.required_,
            exclude_if_none=True,
        )
    return properties


PublicPatientPayload = type('PublicPatientPayload', (BasePublicPatientPayload,),
                            get_payload_properties('public'))

PrivatePatientPayload = type('PublicPatientPayload', (BasePrivatePatientPayload,),
                             get_payload_properties('private'))


def get_patient_payload(person_case, episode_case):
    if person_case.get_case_property(ENROLLED_IN_PRIVATE) == 'true':
        return PrivatePatientPayload.create(person_case, episode_case)
    else:
        return PublicPatientPayload.create(person_case, episode_case)


def _get_phone_numbers(case_properties):
    numbers = []
    for potential_number in NINETYNINEDOTS_NUMBERS:
        number = _parse_number(case_properties.get(potential_number))
        if number:
            numbers.append(_format_number(number))
    return ", ".join(numbers) if numbers else None


def _parse_number(number):
    if number:
        return phonenumbers.parse(number, "IN")


def _format_number(phonenumber):
    if phonenumber:
        return phonenumbers.format_number(
            phonenumber,
            phonenumbers.PhoneNumberFormat.INTERNATIONAL
        ).replace(" ", "")
