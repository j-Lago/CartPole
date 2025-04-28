
class DraggableController:
    _instance = None
    _draggable_instances = []

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance


    @staticmethod
    def another_on_focus(instance):
        for other in DraggableController._draggable_instances:
            if (other is not instance) and other.on_focus:
                return True
        return False

    @staticmethod
    def register_instance(instance):
        DraggableController._draggable_instances.append(instance)


    def __call__(self):
        return DraggableController._instance
