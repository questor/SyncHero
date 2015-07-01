
import yaml
import argparse
import hashlib

def hashfile(afile, hasher, blocksize=65536):
    buf = afile.read(blocksize)
    while len(buf) > 0:
        hasher.update(buf)
        buf = afile.read(blocksize)
    afile.close()
    return hasher.hexdigest()


stream = open("test.yaml", "r")
doc = yaml.load(stream)
for k,v in doc.items():
    print(k, "->", v)
print("\n")



parser = argparse.ArgumentParser(description='SyncHero')
parser.add_argument('-h', '--help', help='print usage', dest='help')
parser.add_argument('-c', '--check-repos', help='check for updates in the repositories', dest='check')
parser.add_argument('-s', '--sync-updates', help='check for updates and sync to new versions', dest='sync')
#parser.add_argument('-p', '--push', help='push all repos back onto server', dest='push')
parser.add_argument('-r', '--reverse-copy', help='reverse copy of files moved during sync', dest='revcopy')
args = parser.parse_args()

print(hashfile(open('test.yaml', 'rb'), hashlib.md5()))


if args.check:
    pass
elif args.sync:
    pass
elif args.push:
    pass
elif args.revcopy:
    pass
else:
    parser.print_help()
