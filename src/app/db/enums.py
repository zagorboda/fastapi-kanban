import enum


class CardHistoryActions(enum.Enum):
    create = 'create'
    update = 'update'
    delete = 'delete'
    move = 'move'

    def __repr__(self):
        return str(self.value)

    def __str__(self):
        return str(self.value)
