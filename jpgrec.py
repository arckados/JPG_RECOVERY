
import os
from threading import Thread

jpgstart = b'\xff\xd8\xff\xe0\x00\x10\x4a\x46'
jpgend = b'\xff\xd9'

def creatdir(path):
    if not os.path.exists(path):
        os.makedirs(path)


class fileobg:

    def __init__(self, orgpath, start, end, data=None):
        self.start = start
        self.end = end
        self.size = end - start
        self.data = data
        self.endstr = "jpg"
        self.orgpath = orgpath

    def getdata(self):
        return self.data

    def save(self, name):
        try:
            path = f"./{self.endstr}/"
            creatdir(path)
            with open(path + f"{name}.{self.endstr}", "wb") as out_file:
                out_file.write(self.data)
            return True
        except Exception as e:
            print(e)
            return False





class fileReco:

    def __init__(self, path="", buffer=2 ** 20):
        self.path = path
        self.buffer = buffer
        self.filecount = 111100
        self.switch = True
        self.searching = False
        self.results = []
        self.totalsearched = 0
        self.currentpos = 0

    def set_path(self, path):
        self.path = f"\\\\.\\{path}:"

    def get_result(self):
        return self.results.copy()

    def findin(self, chunk, start, end, filepos, chunkpos=0):

        startindex = chunk[chunkpos:].find(start)
        if startindex > 0:
            endindex = chunk[chunkpos + startindex:].find(end)
            if endindex > 0:
                realstart = filepos + startindex + chunkpos
                realend = filepos + startindex + endindex + chunkpos + len(end)
                data = chunk[startindex + chunkpos:startindex + chunkpos + endindex + len(end)]
                newfile = fileobg(self.path, realstart, realend, data)
                print(
                    'Found JPG at location: start ' + str(newfile.start) + ' end : ' + str(newfile.end) + " size is  ",
                    newfile.size)

                self.results.append(newfile)

                return chunkpos + startindex + endindex + len(end)
            else:
                return -1
        else:
            return 0

    def getdata(self, file, chunk=None):
        try:
            newdata = file.read(self.buffer)

            self.totalsearched += self.buffer
            if chunk is not None:
                return chunk + newdata
            else:
                return newdata
        except Exception as e:
            print(e, "  ", self.totalsearched / 1024)
            self.totalsearched += self.buffer
            self.seek(file)
            return self.getdata(file, chunk)

    def seek(self, file):
        try:
            self.totalsearched += self.buffer
            file.seek(self.totalsearched)

        except Exception as e:
            print(e, "  ", self.totalsearched / 1024)

    def startthread(self):
        Thread(target=self.start).start()

    def start(self):
        self.searching = True
        print("started")
        try:
            with open(self.path, "rb") as in_file:
                self.switch = True
                counter = 0
                chunk = self.getdata(in_file)
                chunkpos = 0
                while self.switch and len(chunk) > 0:
                    filepos = in_file.tell() - self.buffer
                    pos = self.findin(chunk, jpgstart, jpgend, filepos, chunkpos)
                    if pos > 0:
                        counter += 1
                        chunkpos = pos
                        if counter == self.filecount:
                            self.switch = False
                    elif pos == -1:
                        chunk = self.getdata(in_file, chunk)
                    else:
                        chunkpos = 0
                        chunk = self.getdata(in_file)
        except Exception as e:
            print(e,"failed to open the drive")
        self.searching = False
        print("finished")

    def savealljpg(self):

        for i, img in enumerate(self.results):
            if self.savetoram:
                img.save(str(i))
            else:
                img.savefromfile(i)

    def stop(self):
        self.switch = False


