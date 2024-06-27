from Util import Reader, get_ffxiv_path

class SqPack:
	def __init__(self):
		self.sqpackpath = f"{get_ffxiv_path()}/game/sqpack/ffxiv/"

	def parse_sqpack(self):
		with Reader.open(f"{self.sqpackpath}/000000.win32.index") as index:
			magic = index.read(8)
			platform = index.read(1)
			padding = index.read(3)
			size = index.readUInt32()
			version = index.readUInt32()
			type = index.readUInt32()
			print(size)
			print(version)
			print(type)