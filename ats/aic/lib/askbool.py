
from six.moves import input


def askbool(question, default=False):
    defmsg = ['[y/N]', '[Y/n]']
    while True:
        answer = input('AIC: %s %s ' % (question, defmsg[default])).strip().lower()
        if not answer:
            return default
        if answer == 'y':
            return True
        if answer == 'n':
            return False
