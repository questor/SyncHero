
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

def readconfig():
    stream = open("test.yaml", "r")
    doc = yaml.load(stream)
    for k,v in doc.items():
        print(k, "->", v)
    print("\n")

parser = argparse.ArgumentParser(description='SyncHero')
parser.add_argument('-c', '--check-repos', help='check for updates in the repositories', action='store_true')
parser.add_argument('-s', '--sync-updates', help='check for updates and sync to new versions', action='store_true')
#parser.add_argument('-p', '--push', help='push all repos back onto server', action='store_true')
parser.add_argument('-r', '--reverse-copy', help='reverse copy of files moved during sync', action='store_true')
args = parser.parse_args()

#print(hashfile(open('test.yaml', 'rb'), hashlib.md5()))

if args.check_repos:
    readconfig()
    pass
elif args.sync_updates:
    readconfig()
    pass
#elif args.push:
#    readconfig()
#    pass
elif args.reverse_copy:
    readconfig()
    pass
else:
    parser.print_help()
