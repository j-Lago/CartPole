
class DragLock:
    _draggable_instances = []

    def __init__(self):
        raise PermissionError("A classe 'DraggableController' não deve ser instanciada.")

    @staticmethod
    def another_on_focus(instance):
        for other in DragLock._draggable_instances:
            if (other is not instance) and other.on_focus and other.active:
                return True
        return False

    @staticmethod
    def register_instance(instance):
        DragLock._draggable_instances.append(instance)

