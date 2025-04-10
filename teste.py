class Meta(type):
    def __call__(cls, *args, **kwargs):
        print('Meta.__call__()')
        instance = super().__call__(*args, **kwargs)
        instance.loop()
        return instance


class Base(metaclass=Meta):
    def __init__(self):
        print('Base.__init__()')

    def loop(self):
        print('Base.loop()')


class Subclass(Base):
    def __init__(self):
        super().__init__()
        print("Subclass.__init__()")


if __name__ == '__main__':
    # Test instances
    subclass_instance = Subclass()