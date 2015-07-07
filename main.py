
# based on the same idea like peru, but here the sub-repos are directly pushable back to the source


import yaml
import argparse
import hashlib

import subprocess
import os
import shutil

class Git:
    @staticmethod
    def callGit(directory, *args):
        command=['git']
        if(directory):
            command.append('-C')
            command.append(directory)
        command.extend(args)

        stdout = subprocess.PIPE
        process = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=stdout,universal_newlines=True)
        output, _ = process.communicate()
        if process.returncode != 0:
            raise RuntimeError('Command exited with error code {0}:\n$ {1}\n {2}'.format(process.returncode, ' '.join(command), output))
        return output

    @staticmethod
    def syncToRev(url, directory, revision):
        # TODO: check for subrepos
        if os.path.exists(dir):
            Git.callGit(directory, 'fetch')
        else:
            print("repopath {0} not found, initial clone running".format(dir))
            os.makedirs(directory, exist_ok=True)
            try:
                Git.callGit(None, 'clone', '--progress', url, directory)
            except:
                shutil.rmtree(directory)
                raise
        Git.callGit(directory, 'reset', '--hard', revision)

    @staticmethod
    def push(url, directory):
        pass

    @staticmethod
    def getLatestRevisionOnline(directory, url):
        Git.callGit(directory, 'fetch')
        return Git.callGit(directory, 'rev-parse', '@{u}')

    @staticmethod
    def getCurrentSyncedRevision(directory):
        rev = Git.callGit(directory, 'rev-parse', '@')
        return rev

#-------------------------------------------------------------------
class Hg:
    @staticmethod
    def callHg(directory, *args):
        command=['hg']
        if(directory):
            command.append('--repository')
            command.append(directory)
        command.extend(args)

        stdout = subprocess.PIPE
        process = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=stdout,universal_newlines=True)
        output, _ = process.communicate()
        if process.returncode != 0:
            raise RuntimeError('Command exited with error code {0}:\n$ {1}\n {2}'.format(process.returncode, ' '.join(command), output))
        return output

    @staticmethod
    def syncToRev(url, directory, revision):
        # TODO: check for subrepos
        if os.path.exists(dir):
            Hg.callHg(directory, 'pull')
        else:
            print("repopath {0} not found, initial clone running".format(dir))
            os.makedirs(directory, exist_ok=True)
            try:
                Hg.callHg(None, 'clone', url, directory)
            except:
                shutil.rmtree(directory)
                raise
        Hg.callHg(directory, 'update', '--rev', revision)

    @staticmethod
    def push(url, directory):
        pass

    @staticmethod
    def getLatestRevisionOnline(directory, url):
        Hg.callHg(directory, 'pull')
        return Hg.callHg(directory, 'identify', '--id', '--rev', 'tip')

    @staticmethod
    def getCurrentSyncedRevision(directory):
        return Hg.callHg(directory, 'identify', '--id')

#-------------------------------------------------------------------

def hashfile(afile, hasher, blocksize=65536):
    buf = afile.read(blocksize)
    while len(buf) > 0:
        hasher.update(buf)
        buf = afile.read(blocksize)
    afile.close()
    return hasher.hexdigest()


def readconfig():
    global config
    stream = open("test.yaml", "r")
    config = yaml.load(stream)
    #for k,v in doc.items():
    #    print(k, "->", v)
    #print("\n")

print("SyncHero V0.3")

config = None

# In Python versions prior to 3.4, __file__ returns a relative path. This path
# is fixed at load time, so if the program later cd's (as we do in tests, at
# least) __file__ is no longer valid. As a workaround, compute the absolute
# path at load time.
MODULE_ROOT = os.path.abspath(os.path.dirname(__file__))

parser = argparse.ArgumentParser(description='SyncHero')
parser.add_argument('-c', '--check-repos', help='check for updates in the repositories', action='store_true')
parser.add_argument('-s', '--sync', help='sync to revisions from config file', action='store_true')
#parser.add_argument('-p', '--push', help='push all repos back onto server', action='store_true')
parser.add_argument('-r', '--reverse-copy', help='reverse copy of files moved during sync', action='store_true')
args = parser.parse_args()

#print(hashfile(open('test.yaml', 'rb'), hashlib.md5()))

if args.check_repos:
    readconfig()
    for k,v in config.items():
        dir = os.path.join(MODULE_ROOT, "".join(v['dir']))

        if('fixed-rev' in v):
            print("skipping repo {0} because of fixed-rev".format(v['dir'].rstrip()))
            continue

        if('git' in v):
            syncedRev = Git.getCurrentSyncedRevision(dir)
            latestRev = Git.getLatestRevisionOnline(dir, v['git'])
            baseRev = Git.callGit(dir, 'merge-base', '@', '@{u}')
            if syncedRev == latestRev:
                print("repo {0} is up to date".format(v['dir']))
            elif syncedRev == baseRev:
                print("repo {0} need to pull(latest commit:{1})".format(v['dir'], latestRev.rstrip()))
            elif latestRev == baseRev:
                print("repo {0} need to push".format(v['dir']))
            else:
                print("repo {0} has diverged".format(v['dir']))
        if('hg' in v):
            syncedRev = Hg.getCurrentSyncedRevision(dir)
            latestRev = Hg.getLatestRevisionOnline(dir, v['hg'])
            if syncedRev == latestRev:
                print("repo {0} is up to date".format(v['dir']))
            else:
                print("repo {0} needs push/pull".format(v['dir']))
elif args.sync:
    readconfig()
    # sync repos
    for k,v in config.items():
        dir = os.path.join(MODULE_ROOT, "".join(v['dir']))
        rev = -1
        if('rev' in v):
            rev = v['rev']
        if('fixed-rev' in v):
            rev = v['fixed-rev']
        if rev == -1:
            print('no revision found for repo {0}'.format(v['dir']))
            raise

        if('git' in v):
            Git.syncToRev(v['git'], dir, rev)
        if('hg' in v):
            Hg.syncToRev(v['hg'], dir, rev)

    # copy files
    for k,v in config.items():
        dir = os.path.join(MODULE_ROOT, "".join(v['dir']))


#elif args.push:
#    readconfig()
elif args.reverse_copy:
    readconfig()
    # reverse-copy files
else:
    parser.print_help()
