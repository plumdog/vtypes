from datetime import date, datetime, time


class Validator(object):

    def __init__(self, **vs):
        self.vs = vs

    def add(self, **vs):
        all_vs = self.vs.copy()
        for k, v in vs.items():
            all_vs[k] = v
        return self.__class__(**all_vs)

    def remove(self, *keys):
        all_vs = self.vs.copy()
        for k in keys:
            all_vs.pop(k)
        return self.__class__(**all_vs)

    def _coerce(self, params, to_types=False):
        coerced = {}
        all_keys = set(params.keys())

        for key, vtype in self.vs.items():
            param = params.get(key, vtype.default)
            if vtype.required and (param is None):
                raise ValueError('Missing required value for {}'.format(key))
            try:
                if to_types:
                    value = vtype.coerce_to_type(param)
                else:
                    value = vtype.coerce_to_string(param)
            except Exception as exc:
                raise ValueError('Unable to load value for {!r}: {!r}'.format(key, param)) from exc
                
            coerced[key] = value
            all_keys.discard(key)
        if all_keys:
            raise ValueError('Unexpected arguments: {}'.format(all_keys))
        return coerced

    def to_types(self, params):
        return self._coerce(params, to_types=True)

    def to_strings(self, params):
        return self._coerce(params, to_types=False)


class VType(object):
    type = None
    required = True
    default = None
    settable = True
    extra_init_kwargs = ()

    def __init__(self, required=True, default=None, settable=True, **kwargs):
        self.required = required
        self.default = default
        self.settable = settable

        if not self.settable and (self.default is None):
            raise ValueError('Must set default for non-settable field.')

        for key in self.extra_init_kwargs:
            setattr(self, key, None)

        for key, value in kwargs.items():
            if key not in self.extra_init_kwargs:
                raise TypeError('Unexpected kwarg {}'.format(key))
            setattr(self, key, value)

    @property
    def clsname(self):
        return self.__class__.__name__

    def coerce_to_string(self, value):
        try:
            typed_value = self._coerce_string_to_type(value)
        except TypeError:
            typed_value = value
        return self._coerce_type_to_string(typed_value)

    def coerce_to_type(self, value):
        try:
            str_value = self._coerce_type_to_string(value)
        except TypeError:
            str_value = value
        return self._coerce_string_to_type(str_value)

    def _check_type(self, value, type_):
        if not self.required and (value is None):
            return

        # Type must be exactly correct, not a subclass.
        if type(value) is not type_:
            raise TypeError('{!r} is not type {}.'.format(value, type_))

    def _check_typed_value(self, value):
        try:
            self.check_typed_value(value)
        except ValueError:
            raise
        except Exception as exc:
            msg = 'Typed value {!r} did not pass check for {}'.format(value, self.clsname)
            raise ValueError(msg) from exc
        return

    def check_typed_value(self, value):
        # Given the typed value, check if it is OK. Raise a ValueError
        # if not.
        return

    def _coerce_type_to_string(self, value):
        if not self.required and (value is None):
            return ''
        self._check_type(value, self.type)
        self._check_typed_value(value)
        out = self.coerce_type_to_string(value)
        self._check_type(out, str)
        return out

    def _coerce_string_to_type(self, value):
        if not self.required and not value:
            return None
        self._check_type(value, str)
        out = self.coerce_string_to_type(value)
        self._check_type(out, self.type)
        self._check_typed_value(out)
        return out

    def coerce_type_to_string(self, value):
        return str(value)

    def coerce_string_to_type(self, value):
        return self.type(value)


class VString(VType):
    type = str


class VInt(VType):
    type = int


class VBool(VType):
    type = bool
    false_values = ('', 'false')

    def coerce_type_to_string(self, value):
        if value:
            return '1'
        return ''

    def coerce_string_to_type(self, value):
        is_false = (value.lower() in self.false_values)
        return not is_false


class VUnsignedInt(VInt):
    def check_typed_value(self, value):
        if value < 0:
            raise ValueError('Value for {} must be >= 0')


class VNonStringableMixin(object):

    def coerce_to_type(self, value):
        self._check_type(value, self.type)
        return value

    def coerce_to_string(self, value):
        raise TypeError('Cannot coerce {} to string.'.format(self.type))

class VDict(VNonStringableMixin, VType):
    type = dict


class VValidatorDict(VDict):
    extra_init_kwargs = ['validator']

    def coerce_to_type(self, value):
        value = super().coerce_to_type(value)
        if not self.validator:
            raise AttributeError('Missing validator for {}'.format(self.clsname))
        return self.validator.to_types(value)


class VList(VNonStringableMixin, VType):
    type = list
    extra_init_kwargs = ['of']

    def coerce_to_type(self, value):
        value = super().coerce_to_type(value)
        if not self.of:
            return value
        return self.type(self.of.coerce_to_type(item) for item in value)


class VDTBase(VType):
    allowed_formats = []
    type = None

    def coerce_type_to_string(self, value):
        return value.isoformat()

    def coerce_string_to_type(self, value):
        for format in self.allowed_formats:
            try:
                dt = datetime.strptime(value, format)
            except ValueError:
                continue
            if type(dt) == self.type:
                return dt

            conv_method = getattr(dt, self.type.__name__)
            return conv_method()
                
        raise ValueError(
            'Unable to parse {value} with allowed formats ({allowed_formats})'.format(
                value=value,
                allowed_formats=self.allowed_formats))


class VDate(VDTBase):
    allowed_formats = [
        '%Y-%m-%d',
    ]
    type = date


class VDateTime(VDTBase):
    allowed_formats = [
        '%Y-%m-%dT%H:%M:%S.%fZ',
        '%Y-%m-%dT%H:%M:%S.%f',
        '%Y-%m-%dT%H:%M:%SZ',
        '%Y-%m-%dT%H:%M:%S',
    ]
    type = datetime


class VTime(VDTBase):
    allowed_formats = [
        '%H:%M:%S.%f',
        '%H:%M:%S',
    ]
    type = time
