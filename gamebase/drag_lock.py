
class DragLock:
    _draggable_instances = []

    def __init__(self):
        raise PermissionError("A classe 'DraggableController' não deve ser instanciada.")

    @staticmethod
    def another_on_focus(instance) -> bool:
        for other in DragLock._draggable_instances:
            if (other is not instance) and other.on_focus and other.active:
                return True
        return False

    @staticmethod
    def register_instance(instance) -> None:
        DragLock._draggable_instances.append(instance)

    @staticmethod
    def remove(instance) -> bool:
        for i, it in enumerate(DragLock._draggable_instances):
            if it is instance:
                del DragLock._draggable_instances[i]
                return True
        return False


