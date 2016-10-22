from unittest import TestCase
from datetime import date, datetime, time

from vtypes import (
    Validator,
    VType,
    VString,
    VInt,
    VBool,
    VUnsignedInt,
    VDict,
    VValidatorDict,
    VList,
    VDate,
    VDateTime,
    VTime,
)


class _VTypeBase(object):
    validator = None
    vtype = None
    vkey = None
    vtype_kwargs = {}

    # List of two-tuples, first being input, second being expected output
    ok_to_strings = None
    ok_to_types = None
    # List of bad inputs
    bad_to_strings = None
    bad_to_types = None

    def setUp(self):
        if not self.vkey:
            clsname = self.__class__.__name__
            pre = 'V'
            end = 'TestCase'
            if clsname.startswith(pre) and clsname.endswith(end):
                self.vkey = 'my' + clsname[len(pre):-len(end)].lower()

        if not self.validator:
            if not self.vkey:
                raise ValueError('Unable to guess at vkey.')

            if isinstance(self.vtype, type):
                vtype = self.vtype(**self.vtype_kwargs)
            elif isinstance(self.vtype, VType):
                vtype = self.vtype
            else:
                raise TypeError('Unexpected type for vtype: {!r}'.format(self.vtype))
            kwargs = {self.vkey: vtype}
            self.validator = Validator(**kwargs)

    def _get_for_kind(self, kind, attr_kind):
        
        values_attr_format = '{attr_kind}_to_{kind}'
        if kind == 'string':
            validator_method = self.validator.to_strings
            name = 'strings'
            values_attr = values_attr_format.format(attr_kind=attr_kind, kind=name)
        elif kind == 'type':
            validator_method = self.validator.to_types
            name = 'types'
            values_attr = values_attr_format.format(attr_kind=attr_kind, kind=name)
        else:
            raise ValueError('Must set kind to be "string" or "type".')
        values = getattr(self, values_attr)
        return values, validator_method, name

    def _check_ok(self, string_or_type):
        values, validator_method, name = self._get_for_kind(string_or_type, 'ok')
        for input_, expected_output in values:
            found_output = validator_method(input_)
            msg = 'Conversion to {} failed:\n{!r}\n!=\n{!r}'.format(name, found_output, expected_output)
            self.assertEqual(found_output, expected_output, msg=msg)

    def test_ok_to_strings(self):
        self._check_ok('string')

    def test_ok_to_types(self):
        self._check_ok('type')

    def _check_bad(self, string_or_type):
        values, validator_method, name = self._get_for_kind(string_or_type, 'bad')

        for bad_value in values:
            try:
                output = validator_method(bad_value)
            except ValueError as exc:
                # That's good.
                good_message_prefixes = [
                    'Missing required value for ',
                    'Unable to load value for ',
                    'Unexpected arguments: ',
                ]
                for prefix in good_message_prefixes:
                    if str(exc).startswith(prefix):
                        break
                else:
                    self.fail('Bad exception message:\n{!r}'.format(exc))
            else:
                self.fail(
                    'Did not raise error converting to {}:\n{!r}\ngave:\n{!r}'.format(
                        name, bad_value, output))

    def test_bad_to_strings(self):
        self._check_bad('string')

    def test_bad_to_types(self):
        self._check_bad('type')


class VStringTestCase(_VTypeBase, TestCase):

    vtype = VString

    ok_to_strings = [
        (dict(mystring='stringhere'),
         dict(mystring='stringhere')),
    ]
    ok_to_types = [
        (dict(mystring='stringhere'),
         dict(mystring='stringhere')),
    ]
    bad_to_strings = [
        dict(),
        dict(other='stringhere'),
        # TODO: is this correct?
        # dict(mystring=''),
    ]
    bad_to_types = [
        dict(),
        dict(other='stringhere'),
        # TODO: is this correct?
        # dict(mystring=''),
    ]


class VIntTestCase(_VTypeBase, TestCase):

    vtype = VInt

    ok_to_strings = [
        (dict(myint=1), dict(myint='1')),
        (dict(myint='1'), dict(myint='1')),
        (dict(myint=-1), dict(myint='-1')),
        (dict(myint='-1'), dict(myint='-1')),
    ]
    ok_to_types = [
        (dict(myint='1'), dict(myint=1)),
        (dict(myint=1), dict(myint=1)),
        (dict(myint='-1'), dict(myint=-1)),
        (dict(myint=-1), dict(myint=-1)),
    ]
    bad_to_strings = [
        dict(),
        dict(other=1),
        dict(myint=None),
    ]
    bad_to_types = [
        dict(),
        dict(other='1'),
        dict(myint='not-an-int'),
        dict(myint='one'),
    ]


class VBoolTestCase(_VTypeBase, TestCase):

    vtype = VBool

    ok_to_strings = [
        (dict(mybool=True), dict(mybool='1')),
        (dict(mybool='1'), dict(mybool='1')),
        (dict(mybool='yes'), dict(mybool='1')),
        (dict(mybool=False), dict(mybool='')),
        (dict(mybool=''), dict(mybool='')),
        (dict(mybool='false'), dict(mybool='')),
    ]
    ok_to_types = [
        (dict(mybool='1'), dict(mybool=True)),
        (dict(mybool='false'), dict(mybool=False)),
        (dict(mybool='False'), dict(mybool=False)),
        (dict(mybool='FALSE'), dict(mybool=False)),
        (dict(mybool=True), dict(mybool=True)),
    ]
    bad_to_strings = [
        dict(),
        dict(other=True),
        dict(other=False),
    ]
    bad_to_types = [
        dict(other='1'),
        dict(mybool=1),
        dict(mybool=None),
    ]


class VUnsignedIntTestCase(_VTypeBase, TestCase):

    vtype = VUnsignedInt

    ok_to_strings = [
        (dict(myunsignedint=1), dict(myunsignedint='1')),
        (dict(myunsignedint='1'), dict(myunsignedint='1')),
    ]
    ok_to_types = [
        (dict(myunsignedint='1'), dict(myunsignedint=1)),
        (dict(myunsignedint=1), dict(myunsignedint=1)),
    ]
    bad_to_strings = [
        dict(),
        dict(other=1),
        dict(myunsignedint=None),
        dict(myunsignedint=-1),
    ]
    bad_to_types = [
        dict(),
        dict(other='1'),
        dict(myunsignedint='not-an-int'),
        dict(myunsignedint='one'),
        dict(myunsignedint='-1'),
    ]


class VDictTestCase(_VTypeBase, TestCase):

    vtype = VDict

    ok_to_strings = []
    ok_to_types = [
        (dict(mydict=dict()),
         dict(mydict=dict())),
        (dict(mydict=dict(a=1)),
         dict(mydict=dict(a=1))),
        (dict(mydict=dict(a=1, b=2)),
         dict(mydict=dict(a=1, b=2))),
    ]
    bad_to_strings = [
        dict(),
        dict(mydict=dict(a=1)),
        dict(mydict=None),
        dict(mydict='{"a": "a"}'),
    ]
    bad_to_types = [
        dict(),
        dict(other=dict(a=1)),
        dict(mydict=None),
        dict(mydict='{"a": "a"}'),
    ]


class VValidatorDictTestCase(_VTypeBase, TestCase):

    vtype = VValidatorDict(
        validator=Validator(
            mydate=VDate(),
            mystring=VString(),
        ),
    )
    vkey = 'myvdict'

    ok_to_strings = []
    ok_to_types = [
        (dict(myvdict=dict(mydate='2016-10-22', mystring='string')),
         dict(myvdict=dict(mydate=date(2016, 10, 22), mystring='string'))),
        (dict(myvdict=dict(mydate=date(2016, 10, 22), mystring='string')),
         dict(myvdict=dict(mydate=date(2016, 10, 22), mystring='string'))),
    ]
    bad_to_strings = [
        dict(myvdict=dict(mydate='2016-10-22', mystring='string'), extra='here'),
        dict(myvdict=dict(mydate='2016-10-22', other='string')),
        dict(myvdict=dict(mydate='bad-date', mystring='string')),
    ]
    bad_to_types = [
        dict(myvdict=dict(mydate='2016-10-22', mystring='string'), extra='here'),
        dict(myvdict=dict(mydate='2016-10-22', other='string')),
        dict(myvdict=dict(mydate='bad-date', mystring='string')),
    ]


class VListTestCase(_VTypeBase, TestCase):

    vtype = VList

    ok_to_strings = []
    ok_to_types = [
        (dict(mylist=[]),
         dict(mylist=[])),
        (dict(mylist=['a']),
         dict(mylist=['a'])),
        (dict(mylist=['a', 1]),
         dict(mylist=['a', 1])),
    ]
    bad_to_strings = [
        dict(),
        dict(mylist=['a', 'b']),
        dict(mylist=('a', 'b')),
        dict(mylist=None),
        dict(mylist='["a", "a"]'),
    ]
    bad_to_types = [
        dict(),
        dict(other=['a', 'b']),
        dict(mylist=('a', 'b')),
        dict(mylist=None),
        dict(mylist='["a", "b"]'),
    ]


class VListOfTestCase(_VTypeBase, TestCase):

    vtype = VList(of=VDateTime())

    ok_to_strings = []
    ok_to_types = [
        (dict(mylistof=[]),
         dict(mylistof=[])),
        (dict(mylistof=['2016-10-22T10:30:03']),
         dict(mylistof=[datetime(2016, 10, 22, hour=10, minute=30, second=3)])),
    ]
    bad_to_strings = [
        dict(),
        dict(mylistof=('2016-10-22T10:30:03',)),
        dict(mylistof=[datetime(2016, 10, 22, hour=10, minute=30, second=3)]),
        dict(mylistof=['a', 'b']),
        dict(mylistof=None),
        dict(mylistof='["2016-10-22T10:30:03"]'),
    ]
    bad_to_types = [
        dict(),
        dict(mylistof=('2016-10-22T10:30:03',)),
        dict(mylistof=['a', 'b']),
        dict(mylistof=None),
        dict(mylistof='["2016-10-22T10:30:03"]'),
    ]



class VDateTestCase(_VTypeBase, TestCase):

    vtype = VDate

    ok_to_strings = [
        (dict(mydate=date(2016, 10, 22)),
         dict(mydate='2016-10-22')),
        (dict(mydate='2016-10-22'),
         dict(mydate='2016-10-22')),
    ]
    ok_to_types = [
        (dict(mydate='2016-10-22'),
         dict(mydate=date(2016, 10, 22))),
        (dict(mydate=date(2016, 10, 22)),
         dict(mydate=date(2016, 10, 22))),
    ]
    bad_to_strings = [
        dict(),
        dict(mydate=(2016, 10, 22)),
        dict(mydate=None),
    ]
    bad_to_types = [
        dict(),
        dict(other='2016-10-22'),
        dict(mydate='22/10/2016'),
        dict(mydate=None),
        dict(mydate='not-a-date'),
    ]


class VDateTimeTestCase(_VTypeBase, TestCase):

    vtype = VDateTime

    ok_to_strings = [
        (dict(mydatetime=datetime(2016, 10, 22, hour=10, minute=30, second=3)),
         dict(mydatetime='2016-10-22T10:30:03')),
        (dict(mydatetime='2016-10-22T10:30:03'),
         dict(mydatetime='2016-10-22T10:30:03')),
    ]
    ok_to_types = [
        (dict(mydatetime='2016-10-22T10:30:03'),
         dict(mydatetime=datetime(2016, 10, 22, hour=10, minute=30, second=3))),
        (dict(mydatetime='2016-10-22T10:30:03Z'),
         dict(mydatetime=datetime(2016, 10, 22, hour=10, minute=30, second=3))),
        (dict(mydatetime='2016-10-22T10:30:03.12'),
         dict(mydatetime=datetime(2016, 10, 22, hour=10, minute=30, second=3, microsecond=120000))),
        (dict(mydatetime='2016-10-22T10:30:03.12Z'),
         dict(mydatetime=datetime(2016, 10, 22, hour=10, minute=30, second=3, microsecond=120000))),
        (dict(mydatetime=datetime(2016, 10, 22, hour=10, minute=30, second=3)),
         dict(mydatetime=datetime(2016, 10, 22, hour=10, minute=30, second=3))),
    ]
    bad_to_strings = [
        dict(),
        dict(mydatetime=(2016, 10, 22, 10, 30, 3)),
        dict(mydatetime=None),
    ]
    bad_to_types = [
        dict(),
        dict(other='2016-10-22T10:30:03'),
        dict(other='2016-10-22 10:30:03'),
        dict(mydatetime='22/10/2016T10:30:03'),
        dict(mydatetime='22/10/2016 10:30:03'),
        dict(mydatetime=None),
        dict(mydatetime='not-a-datetime'),
    ]


class VTimeTestCase(_VTypeBase, TestCase):

    vtype = VTime

    ok_to_strings = [
        (dict(mytime=time(hour=10, minute=30, second=3)),
         dict(mytime='10:30:03')),
        (dict(mytime='10:30:03'),
         dict(mytime='10:30:03')),
    ]
    ok_to_types = [
        (dict(mytime='10:30:03'),
         dict(mytime=time(hour=10, minute=30, second=3))),
        (dict(mytime='10:30:03.12'),
         dict(mytime=time(hour=10, minute=30, second=3, microsecond=120000))),
        (dict(mytime=time(hour=10, minute=30, second=3)),
         dict(mytime=time(hour=10, minute=30, second=3))),
    ]
    bad_to_strings = [
        dict(),
        dict(mytime=(10, 30, 3)),
        dict(mytime=None),
    ]
    bad_to_types = [
        dict(),
        dict(other='10:30:03'),
        dict(other='10:30:03.12'),
        dict(mytime='10:30'),
        dict(mytime='10'),
        dict(mytime=''),
        dict(mytime=None),
        dict(mytime='not-a-time'),
    ]
