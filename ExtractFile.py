from ffxiv.SQPK import SQPK


def test():
	sqpk_instance = SQPK()
	sqpk_instance.parse_sqpack()

if __name__ == "__main__":
	test()