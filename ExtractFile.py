from ffxiv.SqPack import SqPack


def test():
	sqpk_instance = SqPack()
	sqpk_instance.parse_sqpack()

if __name__ == "__main__":
	test()