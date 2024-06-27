from Util import Reader, get_ffxiv_path

class SQPK:
	def __init__(self):
		self.sqpackpath = f"{get_ffxiv_path()}/game/sqpack/ffxiv/"

	def parse_sqpack(self):
		print(self.sqpackpath)
	