import unittest
from final import *

class TestTalentClass(unittest.TestCase):
    def test_class(self):
        actor1 = Talent(nm='Will Smith',dob='Sep 25, 1968',pob='Philadelphia, PA',m1='Bad Boys 3',m2='Bright (2017)',m3='Collateral Beauty',total=33)
        actor2 = Talent(nm='Michael J. Fox',dob='Jun 9, 1961',pob='Edmonton, Alberta, Canada',m1='Back in Time',m2='Being Canadian',m3='Interstate 60',total=21)
        actress1 = Talent(nm='Angelina Jolie',dob='Jun 4, 1975',pob='Los Angeles, CA',m1='The Breadwinner',m2='First They Killed My Father: A Daughter of Cambodia Remembers',m3='Kung Fu Panda 3',total=35)
        actress2 = Talent(nm='Reese Witherspoon',dob='Mar 22, 1976',pob='Nashville, TN',m1='A Wrinkle in Time',m2='Home Again',m3='Sing',total=33)

        self.assertEqual(actor1.name, 'Will Smith')
        self.assertEqual(actor2.movie2, 'Being Canadian')
        self.assertEqual(actress1.birthplace, 'Los Angeles, CA')
        self.assertEqual(actress2.total, 33)
        self.assertEqual(actor1.__str__(), "Will Smith was born on Sep 25, 1968, in Philadelphia, PA, and has most recently appeared in Bad Boys 3, Bright (2017), and Collateral Beauty.")
        self.assertEqual(actor2.__str__(), "Michael J. Fox was born on Jun 9, 1961, in Edmonton, Alberta, Canada, and has most recently appeared in Back in Time, Being Canadian, and Interstate 60.")
        self.assertEqual(actress1.__str__(), "Angelina Jolie was born on Jun 4, 1975, in Los Angeles, CA, and has most recently appeared in The Breadwinner, First They Killed My Father: A Daughter of Cambodia Remembers, and Kung Fu Panda 3.")
        self.assertEqual(actress2.__str__(), "Reese Witherspoon was born on Mar 22, 1976, in Nashville, TN, and has most recently appeared in A Wrinkle in Time, Home Again, and Sing.")

class TestTalentData(unittest.TestCase):
    def test_data(self):
        talent = get_talent_info()

        self.assertEqual(talent[0].name, 'Chris Evans')
        self.assertEqual(talent[8].birthdate, 'Oct 23, 1976')
        self.assertEqual(talent[-1].total, 22)
        self.assertEqual(talent[-2].birthplace, 'Mount Vernon, NY')
        self.assertEqual(talent[30].movie1, 'Justice League (2017)')
        self.assertEqual(talent[40].movie2, 'Guardians of the Galaxy Vol. 2')
        self.assertEqual(talent[0].movie2, talent[1].movie1)
        self.assertEqual(talent[1].birthplace, talent[10].birthplace)
        self.assertEqual(talent[31].total, talent[40].total)

unittest.main()
