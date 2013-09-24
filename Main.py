import datetime
from struct import *
import uuid
import os.path


__author__ = 'Graham Voysey'


class PySim(object):
    __filename = None

    #  header attributes
    __trailerOffset = None
    __magic = long("a57d8ee659dc45ec", 16)
    __timeStepSize = None
    __startTime = None
    __endTime = None
    __creatingUser = None
    __creatingComputer = None
    __scenarioRecord = None
    __platformRecords = None
    __modeRecords = None
    __speciesRecords = None
    __timeStepRecordOffsets = None

    # payload attributes

    def __init__(self, filename):
        if not os.path.exists(filename):
            raise RuntimeError('Simulation file not found')
        self.__filename = filename

    def ReadFooter(self):
        with open(self.__filename, "rb") as l:
            #  preliminary work; read offset and magic number or die.
            b = BinaryStream(l)
            b.base_stream.seek(-16, 2)
            self.__trailerOffset = b.readUInt64()
            magic = long(b.readUInt64())
            if magic != self.__magic:
                raise IOError('magic number not seen at expected location')

            #  read payload of the footer
            b.base_stream.seek(self.__trailerOffset, 0)
            self.__timeStepSize = datetime.timedelta(microseconds=b.readUInt64() / 10)
            self.__startTime = datetime.datetime(1, 1, 1) + datetime.timedelta(microseconds=long(b.readUInt64()) / 10)
            self.__endTime = datetime.datetime(1, 1, 1) + datetime.timedelta(microseconds=long(b.readUInt64()) / 10)
            self.__creatingUser = b.readString()
            self.__creatingComputer = b.readString()
            self.__scenarioRecord = b.readString(), uuid.UUID(bytes=b.readBytes(16))

            platformCount = b.readInt32()
            self.__platformRecords = []
            for i in xrange(0, platformCount):
                self.__platformRecords.append(PlatformRecord(b.readInt32(), b.readString(), uuid.UUID(bytes=b.readBytes(16))))

            modeCount = b.readInt32()
            self.__modeRecords = []
            for i in xrange(0, modeCount):
                self.__modeRecords.append(ModeRecord(b.readInt32(), b.readString(), uuid.UUID(bytes=b.readBytes(16)), uuid.UUID(bytes=b.readBytes(16))))

            speciesCount = b.readInt32()
            self.__speciesRecords = []
            for i in xrange(0, speciesCount):
                self.__speciesRecords.append(SpeciesRecord(b.readInt32(), b.readInt32(), b.readString(), uuid.UUID(bytes=b.readBytes(16))))

            offsetCount = b.readInt32()
            self.__timeStepRecordOffsets = []
            for i in xrange(0, offsetCount):
                self.__timeStepRecordOffsets.append(b.readUInt64())

    def ReadTimeStepRecord(self, offset):
        pass


class PlatformRecord(object):
    actorID = None
    name = None
    guid = None

    def __init__(self, actorID, name, guid):
        self.actorID = actorID
        self.name = name
        self.guid = guid


class ModeRecord(object):
    actorID = None
    name = None
    guid = None
    platformGuid = None

    def __init__(self, actorID, name, guid, platformGuid):
        self.name = name
        self.actorID = actorID
        self.guid = guid
        self.platformGuid = platformGuid


class SpeciesRecord(object):
    animatCount = None
    startActorID = None
    name = None
    guid = None

    def __init__(self, animatCount, startID, name, guid):
        self.animatCount = animatCount
        self.startActorID = startID
        self.name = name
        self.guid = guid


class BinaryStream:
    def __init__(self, base_stream):
        self.base_stream = base_stream

    def readByte(self):
        return self.base_stream.read(1)

    def readBytes(self, length):
        return self.base_stream.read(length)

    def readChar(self):
        return self.unpack('b')

    def readUChar(self):
        return self.unpack('B')

    def readBool(self):
        return self.unpack('?')

    def readInt16(self):
        return self.unpack('h', 2)

    def readUInt16(self):
        return self.unpack('H', 2)

    def readInt32(self):
        return self.unpack('i', 4)

    def readUInt32(self):
        return self.unpack('I', 4)

    def readInt64(self):
        return self.unpack('q', 8)

    def readUInt64(self):
        return self.unpack('Q', 8)

    def readFloat(self):
        return self.unpack('f', 4)

    def readDouble(self):
        return self.unpack('d', 8)

    def readString(self):
        length = self.readStringLength()
        return self.unpack(str(length) + 's', length)

    def readStringLength(self):
        byte = 0x80
        bytes = []
        result = 0
        while byte & 0x80:
            byte = ord(self.base_stream.read(1))
            bytes.append(byte)
        for i in xrange(0, len(bytes)):
            result |= (bytes[i] & 0x7F) << (len(bytes) - 1 - i)*7
        return result

    def read7BitInt(self):
        value = 0
        shift = 0
        while True:
            val = ord(self.base_stream.read(1))
            if val & 128 == 0:
                break
            value |= (val & 0x7F) << shift
            shift += 7
        return value | (val << shift)

    def writeBytes(self, value):
        self.base_stream.write(value)

    def writeChar(self, value):
        self.pack('c', value)

    def writeUChar(self, value):
        self.pack('C', value)

    def writeBool(self, value):
        self.pack('?', value)

    def writeInt16(self, value):
        self.pack('h', value)

    def writeUInt16(self, value):
        self.pack('H', value)

    def writeInt32(self, value):
        self.pack('i', value)

    def writeUInt32(self, value):
        self.pack('I', value)

    def writeInt64(self, value):
        self.pack('q', value)

    def writeUInt64(self, value):
        self.pack('Q', value)

    def writeFloat(self, value):
        self.pack('f', value)

    def writeDouble(self, value):
        self.pack('d', value)

    def writeString(self, value):
        length = len(value)
        self.writeUInt16(length)
        self.pack(str(length) + 's', value)

    def pack(self, fmt, data):
        return self.writeBytes(pack(fmt, data))

    def unpack(self, fmt, length=1):
        return unpack(fmt, self.readBytes(length))[0]


sim = PySim("""C:\Users\Graham Voysey\Desktop\simulation.exposures""")
sim.ReadFooter()