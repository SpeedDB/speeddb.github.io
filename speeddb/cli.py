import argparse
from os.path import abspath, dirname, join

from .database import build_db, destroy_db
from .database import init as db_init

def read(rel_path):
   import codecs
   here = abspath(dirname(__file__))
   with codecs.open(join(here, rel_path), 'r') as fp:
      return fp.read()

def get_version(rel_path):
   for line in read(rel_path).splitlines():
      if line.startswith('__version__'):
         delim = '"' if '"' in line else "'"
         return line.split(delim)[1]

version = get_version("__init__.py")

parser = argparse.ArgumentParser("SpeeddDB", description="SpeedDB CLI")

parser.add_argument('-v', '--version', action='version', version=f'SpeedDB {version}', help='Show version')

command = parser.add_subparsers(title='commands', dest='command')

init = command.add_parser("init", help="Initialize a folder that's used to store databases")
init.add_argument("-n", "--name", type=str, help="Folder Name")

build = command.add_parser("build", help="Build new database")
build.add_argument("name", nargs="+", help="Database Name")
build.add_argument("-m", "--model", type=str, help="Database Model (documents/keyval/...)", required=True)

destroy = command.add_parser("destroy", help="Destroy and delete an entire database (can't be undone)")
destroy.add_argument("name", type=str, help="Database Name")

def runner():
   main(parser.parse_args())

def main(args: argparse.Namespace):
   if args.command == "init":
      db_init(args.name)

   if args.command == "build":
      result = build_db(*args.name, model=args.model)
      if result:
         parser.error(result)

   if args.command == "destroy":
      destroy_db(args.name)

if __name__ == "__main__":
   runner()