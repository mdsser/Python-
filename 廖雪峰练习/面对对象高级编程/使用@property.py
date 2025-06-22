class Student(object):
    @property
    def score(self):
        return self._score

    @score.setter
    def score(self, value):
        if not isinstance(value, int):
            raise ValueError('score must be an integer')
        if value < 0 or value > 100:
            raise ValueError('score must be between 0 ~ 100!')
        self._score = value

s = Student()
# s.set_score(60)
# print(s.get_score())
#
# s.set_score(9999)

s.score = 60
print(s.score)

s.score = 9999