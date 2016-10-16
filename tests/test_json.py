import unittest

from seito.john import obj
from seito.seq import seq
from seito.underscore import _


class Test(unittest.TestCase):
    def test_john_object(self):
        i = obj({'z-index': 1000})

        self.assertEqual(i['z-index'].or_else(0), 1000)
        i['toto'] = [1, 2, 3]
        i.toto = [4, 5, 6]
        self.assertEqual(i.toto.or_none(), [4, 5, 6])

    def test_fail(self):
        i = obj({'toto': 1,
                 'tata': {'2': 3},
                 'titi': [111, 112, 113]
                 })
        v = i.tito.or_else([])

        def custom_print(elem, name='None'):
            print(str(elem) + " " + name)

        i.tito.or_else(seq(1, 2, 3)).for_each(custom_print, name='toto')
        [custom_print(elem, name='toto') for elem in i.get('tito', [1, 2, 3])]

        k = i.tito.or_else([])
        print(k)

    def test_map(self):
        #  m = flist([1, 2, 3]).str_map('pow(_,2)')
        #  print(m)
        class A(object):
            def __init__(self, integer):
                self.x = integer

            def get_test(self):
                return self.x
                # .str_map(
                # 'value = __.get_test()',
                # 'value += 1',
                # 'oreturn = A(value)',
                # r_var='oreturn', env=locals())\


        def t(v, a):
            return A(v).get_test() * a

        ref = 50
        (seq(A(1), A(2), A(3))
            .filter(lambda a: a.get_test() < 2)
            .map(lambda x: t(x.get_test() ** 2 / 1.5, ref))
            .for_each(print)
         )

        print(seq(A(1), A(2), A(3)))
        print(seq([A(1), A(2), A(3)]))

    def test_underscore(self):
        class A(object):
            def __init__(self, integer):
                self.x = integer

            def get_x(self):
                return self.x

            def calc_y(self, z):
                return self.x * z

        print(seq(A(1)).stream()
                  .map(_.calc_y(4))
                  .to_list()
         )








