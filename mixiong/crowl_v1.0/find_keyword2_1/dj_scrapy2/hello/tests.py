from django.test import TestCase

# Create your tests here.
import os

class t1(object):
    def __init__(self):
        pass

    def show1(self):
        print ("self.show")

    def __getattr__(self, item):
        return self.show1()

    def __call__(self, *args):
        print ("__call__")
        print (args)
t=t1()
t.show1()

t.show2()
t("mk")