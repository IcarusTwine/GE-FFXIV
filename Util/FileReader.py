import struct, uuid, io
import numpy as np


_ENDIAN_SYMBOLS = {
	'little': '<',
	'big': '>',
	'native': '@',
	'network': '!'
}

class KeenReader:
	def __init__(self, stream, endianess: str = '<'): # little
		self.base_stream = stream
		self.set_endian(endianess)
		
		self.base_offset = 0
		self.entry_offset = 0
		
		self._marks = []
	
	def set_base_offset(self, n):
		if n >= 0:
			self.base_offset = n
	
	def set_entry_offset(self, n = None):
		if n == None:
			self.entry_offset = self.get_pos()
		elif n >= 0:
			self.entry_offset = n
	
	def mark(self):
		self._marks.append(self.get_pos())
		return self
		
	def pop(self):
		if len(self._marks) > 0:
			return self._marks.pop()
		
	def reset(self, pop = True, *, adjust = 0):
		if len(self._marks) > 0:
			_ = self._marks.pop() if pop else self._marks[-1]
			self.set_pos(_ + adjust)
		return self
		
	@staticmethod
	def open(fn, mode = 'rb', endianess = '<'):
		return KeenReader(open(fn, mode), endianess = endianess)
	
	@staticmethod
	def load(data, endianess = '<'):
		return KeenReader(io.BytesIO(data), endianess = endianess)
	
	def close(self):
		if self.base_stream:
			self.base_stream.close()
			del self.base_stream
	
	def __enter__(self):
		return self
		
	def __exit__(self, exc_type, exc_value, traceback):
		self.close()

	def set_endian(self, endianess):
		if endianess in _ENDIAN_SYMBOLS:
			self._e = _ENDIAN_SYMBOLS[endianess]
		elif len(endianess) == 1:
			self._e = endianess
		else:
			raise Exception(f"Invalid Endianess '{endianess}'")

	def get_pos(self):
		return self.base_stream.tell()
		
	def set_pos(self, p):
		self.base_stream.seek(p)
		return self
		
	def align(self, n = 16):
		if n > 1:
			_ = self.get_pos()
			p = _ - self.entry_offset + self.base_offset
			m = p % n
			if m > 0:
				self.set_pos(_ + n - m)
		return self
			
	def find(self, pattern, *, return_after = False): # TODO: improve speed by chunk reading
		_p = self.get_pos()
		_i, _s = 0, len(pattern)
		
		while True:
			_b = self.base_stream.read(1)
			if not _b:
				break
			if _b == pattern[_i:_i+1]:
				_i += 1
				if _i >= _s:
					if not return_after:
						self.set_pos(self.get_pos() - _i)
					return True
			elif _i != 0: # for overlaps
				self.set_pos(self.get_pos()  - _i)
				_i = 0
		
		self.set_pos(_p)
		return False
		
	def skip(self, n):
		if n != 0:
			self.set_pos(self.get_pos() + n)
		return self
		
	def read(self, n = -1):
		if n > 0:
			return self.base_stream.read(n)
		return self.base_stream.read()
		
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
		return self.unpack(f'{self._e}h', 2)

	def readUInt16(self):
		return self.unpack(f'{self._e}H', 2)

	def readInt32(self):
		return self.unpack(f'{self._e}i', 4)

	def readUInt32(self):
		return self.unpack(f'{self._e}I', 4)

	def readInt64(self):
		return self.unpack(f'{self._e}q', 8)

	def readUInt64(self):
		return self.unpack(f'{self._e}Q', 8)

	def readString(self, length = None):
		if length:
			l = length
		else:
			l = self.readInt32()
		if l < 1:
			return ""
		return self.read(l).decode('utf-8')
		
	def readDefString(self):
		l = self.readUChar()
		return self.read(l + 1).decode('ascii')
		
	def readGUID(self):
		return uuid.UUID(bytes_le = self.readBytes(16))

	def readGUIDGroup(self):
		guid 	= self.readGUID()
		hash32  = self.readUInt32()
		part	= self.readUInt64()
		
		return f"{guid}:{hash32:08x}:{part}"
		
	def readPointer(self, zero_pointer = False):
		_pos = self.get_pos()
		_rel = self.readUInt32()
		if zero_pointer and _rel == 0:
			return 0
		return _pos + _rel
		
	def readVarInt(self):
		shift = 0
		n = 0
		while True:
			i = self.readUChar()
			n |= (i & 0x7f) << shift
			shift += 7;
			if not (i & 0x80):
				break
		return n;
		
	def readFloat(self):
		return self.unpack(f'{self._e}f', 4)
	
	def readHalfFloat(self, endian = 0):
		u = self.read(2)
		uint16_array = np.frombuffer(u, dtype=f'{self._e}u2')
		float16_array = uint16_array.view(np.float16)
		return float(float16_array[0])


	def readDouble(self):
		return self.unpack(f'{self._e}d', 8)

	def unpack(self, fmt, length = 1):
		if self.base_stream:
			return struct.unpack(fmt, self.readBytes(length))[0]
			
	def readStruct(self, format, amount = 1):
		if not self.base_stream:
			return
			
		sz = struct.calcsize(format)
		if amount < 2:
			return struct.unpack(f'{self._e}{format}', self.readBytes(sz))
		else:
			return [ struct.unpack(f'{self._e}{format}', self.readBytes(sz)) for _ in range(amount) ]


	def print(self, with_base = True):
		if with_base:
			print(f'reader @ 0x{self.get_pos() + self.base_offset:08X}')
		else:
			print(f'reader @ 0x{self.get_pos():08X}')