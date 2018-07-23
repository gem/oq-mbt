import json
# import pprint

_Metacls__registry = {}


class Metacls(type):
    __registry = {}

    def __new__(mcs, name, bases, dict):
        global __registry
        ret = type.__new__(mcs, name, bases, dict)
        __registry[name] = ret
        return ret


class Dictable(object):
    __metaclass__ = Metacls

    @staticmethod
    def from_dict(dct):
        cls = _Metacls__registry[dct['__class__']]

        # print("from_dict: %s" % cls.__name__)
        if '__public__' not in vars(cls):
            raise ValueError('for Dictable instance a __public__ '
                             'attribute must be defined')
        args = []
        # print("  class and __public__, \
        # proceed with subclass [%s]" % dct['__class__'])
        for val in cls.__public__:
            if val in dct:
                if isinstance(dct[val], dict) and '__class__' in dct[val]:
                    args.append(Dictable.from_dict(dct[val]))
                else:
                    args.append(cls.deserialize(dct[val]))

        # print("ARGS: ", cls.__name__)
        # print(args)
        return cls(*args)

    def to_dict(self):
        return Dictable.serialize(self)

    def sync_dom(self):
        pass

    def parent_set(self, parent):
        self.parent = parent

    @staticmethod
    def serialize(obj):
        ret = None
        if isinstance(obj, Dictable):
            obj.sync_dom()
            ret = {'__class__': obj.__class__.__name__}
            for i in obj.__public__:
                ret[i] = Dictable.serialize(getattr(obj, i))
        elif isinstance(obj, list):
            ret = []
            for item in obj:
                ret.append(Dictable.serialize(item))
        elif isinstance(obj, dict):
            ret = {}
            for key in obj:
                ret[key] = Dictable.serialize(obj[key])
        else:
            ret = obj

        return ret

    @staticmethod
    def deserialize(dct):
        ret = None
        if isinstance(dct, dict):
            # print("  dict found")
            if '__class__' in dct:
                return Dictable.from_dict(dct)
            else:
                ret = {}
                for key in dct:
                    ret[key] = Dictable.deserialize(dct[key])
        elif isinstance(dct, list):
            # print("  list found")
            ret = []
            for i, value in enumerate(dct):
                # print("    Index %d" % i)
                # print("    value %s" % value)
                # print("    deser [%s]" % Dictable.deserialize(value))
                ret.append(Dictable.deserialize(value))
        else:
            ret = dct

        return ret


if __name__ == '__main__':
    class One(Dictable):
        __public__ = ['a', 'b']

        def __init__(self, a, b):
            # print("One::__init__")
            if not isinstance(b, list):
                raise TypeError
            self.a = a
            self.b = b

        def toDict(self):
            return ({'__class__': self.__class__.__name__,
                     'a': self.a, 'b': self.b})

    class Two(Dictable):
        __public__ = ['c', 'd']

        def __init__(self, c, d):
            # print("Two::__init__")
            if not isinstance(d, list):
                raise TypeError
            self.c = c
            self.d = d

    class Glob(Dictable):
        __public__ = ['x', 'y', 'z']

        def __init__(self, x, y, z):
            if not isinstance(x, One):
                raise TypeError("arg x isn't One class instance")
            elif not isinstance(y, list):
                raise TypeError("arg y isn't a list")
            self.x = x
            self.y = y
            self.z = z

    def main():
        a = {'__class__': 'Glob',
             'x': {'__class__': 'One', 'a': 71, 'b': ['xxx', 'yyy']},
             'y': [{'__class__': 'Two', 'c': 171, 'd': ['1xxx', '1yyy']},
                   {'__class__': 'Two', 'c': 271, 'd': ['2xxx', '2yyy']}],
             'z': 56
             }

        g_o = Glob.from_dict(a)
        print(json.dumps(g_o.to_dict(), sort_keys=True))

    main()
