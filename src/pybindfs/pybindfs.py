import os
import sys
from app import MyApp

def main(args):
    print("args:" + str(args))
    app = MyApp()
    app.run()


if __name__ == '__main__':
    main(sys.argv)
