# based on the same idea like peru, but here the sub-repos are directly pushable back to the source


import yaml
import argparse
import hashlib

import subprocess
import os
import shutil

import urllib.parse as urlparse
import urllib.request as urllib


class Git:
    @staticmethod
    def callGit(directory, *args):
        command = ['git']
        if (directory):
            command.append('-C')
            command.append(directory)
        command.extend(args)

        stdout = subprocess.PIPE
        process = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=stdout, universal_newlines=True)
        output, _ = process.communicate()
        if process.returncode != 0:
            raise RuntimeError(
                'Command exited with error code {0}:\n$ {1}\n {2}'.format(process.returncode, ' '.join(command),
                                                                          output))
        return output

    @staticmethod
    def syncToRev(url, directory, revision):
        # TODO: check for subrepos
        if os.path.exists(directory):
            Git.callGit(directory, 'fetch')
        else:
            print("repopath {0} not found, initial clone running".format(directory))
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


# -------------------------------------------------------------------
class Hg:
    @staticmethod
    def callHg(directory, *args):
        command = ['hg']
        if (directory):
            command.append('--repository')
            command.append(directory)
        command.extend(args)

        stdout = subprocess.PIPE
        process = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=stdout, universal_newlines=True)
        output, _ = process.communicate()
        # 0 is ok, 1 is sometimes also ok (hg incoming or hg outgoing)
        if (process.returncode != 0) and (process.returncode != 1):
            raise RuntimeError(
                'Command exited with error code {0}:\n$ {1}\n {2}'.format(process.returncode, ' '.join(command),
                                                                          output))
        return output

    @staticmethod
    def syncToRev(url, directory, revision):
        # TODO: check for subrepos
        if os.path.exists(directory):
            Hg.callHg(directory, 'pull')
        else:
            print("repopath {0} not found, initial clone running".format(directory))
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


# -------------------------------------------------------------------
def readRepoConfig():
    global repoConfig
    stream = open("test.yaml", "r")
    repoConfig = yaml.load(stream)
    # print("RepoConfig:")
    # for k,v in doc.items():
    #    print(k, "->", v)
    # print("\n")


def readFileCopyState():
    global fileCopyState
    global fileCopyStateIsDirty
    if os.path.isfile(".synchero.filestate"):
        stream = open(".synchero.filestate")
        fileCopyState = yaml.load(stream)
    fileCopyStateIsDirty = False
    # print("FileCopyState:")
    # for k,v in doc.items():
    #    print(k, "->", v)
    # print("\n")


def writeFileCopyState():
    global fileCopyState
    global fileCopyStateIsDirty
    if fileCopyStateIsDirty:
        with open(".synchero.filestate", "w+") as f:
            yaml.dump(fileCopyState, f, default_flow_style=False)


def getFileCopyState(filename):
    global fileCopyState
    statestring = urlparse.urljoin('file:', urllib.pathname2url(filename))
    #print("statestring {0}".format(statestring))
    if statestring in fileCopyState:
        return fileCopyState[statestring]
    else:
        return -1


def setFileCopyState(filename, newstate):
    global fileCopyState
    global fileCopyStateIsDirty
    statestring = urlparse.urljoin('file:', urllib.pathname2url(filename))
    fileCopyState[statestring] = newstate
    fileCopyStateIsDirty = True


def hashfile(afile, hasher, blocksize=65536):
    buf = afile.read(blocksize)
    while len(buf) > 0:
        hasher.update(buf)
        buf = afile.read(blocksize)
    afile.close()
    return hasher.hexdigest()


repoConfig = {}
fileCopyState = {}
fileCopyStateIsDirty = False


def main():
    print("SyncHero V0.3")

    # In Python versions prior to 3.4, __file__ returns a relative path. This path
    # is fixed at load time, so if the program later cd's (as we do in tests, at
    # least) __file__ is no longer valid. As a workaround, compute the absolute
    # path at load time.
    MODULE_ROOT = os.path.abspath(os.path.dirname(__file__))

    parser = argparse.ArgumentParser(description='SyncHero')
    parser.add_argument('-c', '--check-repos', help='check for updates in the repositories', action='store_true')
    parser.add_argument('-s', '--sync', help='sync to revisions from config file', action='store_true')
    # parser.add_argument('-p', '--push', help='push all repos back onto server', action='store_true')
    parser.add_argument('-r', '--reverse-copy', help='reverse copy of files moved during sync', action='store_true')
    args = parser.parse_args()

    if args.check_repos:
        readRepoConfig()
        for k, v in repoConfig.items():
            dir = os.path.join(MODULE_ROOT, "".join(v['dir']))

            if ('fixed-rev' in v):
                print("skipping repo {0} because of fixed-rev".format(v['dir'].rstrip()))
                continue

            if ('git' in v):
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
            if ('hg' in v):
                outputIncoming = Hg.callHg(dir, 'incoming')
                if outputIncoming.find("no changes found") == -1:
                    print("repo {0} found changes on server".format(v['dir']))
                # else:
                #    print("repo {0} found no changes on server".format(v['dir']))

                outputOutgoing = Hg.callHg(dir, 'outgoing')
                if outputOutgoing.find("no changes found") == -1:
                    print("repo {0} found local changes not pushed to server".format(v['dir']))
                    # else:
                    #    print("repo {0} found no local changes not pushed to server".format(v['dir']))

    elif args.sync:
        readRepoConfig()
        readFileCopyState()
        # sync repos
        for k, v in repoConfig.items():
            dir = os.path.join(MODULE_ROOT, "".join(v['dir']))
            rev = -1
            if ('rev' in v):
                rev = v['rev']
            if ('fixed-rev' in v):
                rev = v['fixed-rev']
            if rev == -1:
                print('no revision found for repo {0}'.format(v['dir']))
                raise

            if ('git' in v):
                Git.syncToRev(v['git'], dir, rev)
            if ('hg' in v):
                Hg.syncToRev(v['hg'], dir, rev)

        # copy files
        for k, v in repoConfig.items():
            dir = os.path.join(MODULE_ROOT, "".join(v['dir']))
            if ('copy' in v):
                for i in v['copy']:
                    srcFileName = os.path.abspath(v['dir'] + '/' + i['src'])
                    dstFileName = os.path.abspath(i['dst'])
                    print("copy src {0} to {1}".format(srcFileName, dstFileName))
                    sourceFileState = getFileCopyState(srcFileName)
                    destFileState = getFileCopyState(dstFileName)

                    if os.path.isfile(srcFileName) == False:
                        print("copy src <{0}> not found!".format(srcFileName))
                        raise
                    sourceHash = hashfile(open(srcFileName, 'rb'), hashlib.md5())
                    destHash = -1
                    if os.path.isfile(dstFileName):
                        destHash = hashfile(open(dstFileName, 'rb'), hashlib.md5())

                    if sourceFileState != sourceHash:
                        setFileCopyState(srcFileName, sourceHash)
                        if destFileState == destHash:
                            #print("destHash equals to destFileState, copy is safe!")
                            shutil.copy(srcFileName, dstFileName)
                            setFileCopyState(dstFileName, sourceHash)   # new filehash!
                        else:
                            print("Destination File was changed after last copy, merge file!")
                    else:
                        #print("nothing to do because sourceState equals to sourceHash")
                        if destFileState == destHash:
                            #print("nothing to do, file not modified")
                            pass
                        else:
                            print("Destination File was changed after last copy, do a rev-copy!")
        writeFileCopyState()


    # elif args.push:
    #    readRepoConfig()
    elif args.reverse_copy:
        readRepoConfig()
        readFileCopyState()
        # reverse-copy files

        writeFileCopyState()
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
