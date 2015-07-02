
import yaml
import argparse
import hashlib

import subprocess
import os
import shutil

class Git:
    @staticmethod
    def callGit(*args):
        command=['git']
        #if(gitDir):
        #    command.append('-C {0}'.format(gitDir))
        command.extend(args)

        stdout = subprocess.PIPE
        process = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=stdout,universal_newlines=True)
        output, _ = process.communicate()
        if process.returncode != 0:
            raise RuntimeError('Command exited with error code {0}:\n$ {1}\n {2}'.format(
                process.returncode, ' '.join(command), output
            ))
        return output

    @staticmethod
    def cloneToDir(url, directory, revision):
        # returns the revision synced to
        # TODO: check for subrepos
        os.makedirs(directory, exist_ok=True)
        currentDir = os.getcwd()
        try:
            # git clone git@github.com:whatever folder-name
            Git.callGit('clone', '--progress', url, directory)       # oder fetch?
            os.chdir(directory)
            Git.callGit('checkout', revision)
            os.chdir(currentDir)
        except:
            os.chdir(currentDir)
            shutil.rmtree(directory)
            raise
        return Git.getCurrentSyncedRevision(directory)

    @staticmethod
    def push(url, directory):
        pass

    @staticmethod
    def getLatestRevisionOnline(url):
        pass

    @staticmethod
    def getCurrentSyncedRevision(directory):
        currentDir = os.getcwd()
        os.chdir(directory)
        rev = Git.callGit('log', '--pretty=format:"%h"', '-n 1')
        os.chdir(currentDir)
        return rev

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

config = None

# In Python versions prior to 3.4, __file__ returns a relative path. This path
# is fixed at load time, so if the program later cd's (as we do in tests, at
# least) __file__ is no longer valid. As a workaround, compute the absolute
# path at load time.
MODULE_ROOT = os.path.abspath(os.path.dirname(__file__))

parser = argparse.ArgumentParser(description='SyncHero')
parser.add_argument('-c', '--check-repos', help='check for updates in the repositories', action='store_true')
parser.add_argument('-s', '--sync-updates', help='check for updates and sync to new versions', action='store_true')
#parser.add_argument('-p', '--push', help='push all repos back onto server', action='store_true')
parser.add_argument('-r', '--reverse-copy', help='reverse copy of files moved during sync', action='store_true')
args = parser.parse_args()

#print(hashfile(open('test.yaml', 'rb'), hashlib.md5()))

if args.check_repos:
    readconfig()
    for k,v in config.items():
        dir = os.path.join(MODULE_ROOT, "".join(v['dir']))
        if('git' in v):
            Git.getCurrentSyncedRevision(dir)
        if('hg' in v):
            print(v['hg'])
elif args.sync_updates:
    readconfig()
    # sync repos
    for k,v in config.items():
        dir = os.path.join(MODULE_ROOT, "".join(v['dir']))
        if('git' in v):
            Git.cloneToDir(v['git'], dir, v['rev'])
    # copy files
#elif args.push:
#    readconfig()
elif args.reverse_copy:
    readconfig()
    # reverse-copy files
else:
    parser.print_help()
