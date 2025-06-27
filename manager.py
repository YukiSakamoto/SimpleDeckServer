import yaml
from pathlib import Path

class SpotNotFoundError(Exception):
    def __init__(self, not_found_spot_name):
        self.not_found_spot_name = not_found_spot_name

class OperationError(Exception):
    def __init__(self, code, reason):
        self.code = code
        self.reason = reason
    

class DeckManager:
    def __init__(self, spot_name_list: list, filename = "state.yaml"): #initial_spot_status: list[dict] | None = None):
        self.filepath = Path(filename)
        if self.filepath.exists():
            deck_status = self.load()
            for spot_name in spot_name_list:
                if not spot_name in deck_status:
                    deck_status[spot_name] = None
            self.save(deck_status)
        else:
            deck_status = {}
            for spot_name in spot_name_list:
                deck_status[spot_name] = None
            self.save(deck_status)
    
    def load(self):
        if self.filepath.exists():
            with open(self.filepath, 'r') as f:
                return yaml.safe_load(f) or {}
        else:
            return {}
    def save(self, deck_status: dict):
        with open(self.filepath, 'w') as f:
            yaml.safe_dump(deck_status, f, default_flow_style=False, allow_unicode=True)

    def get_spot_status(self, spot_name):
        deck_status = self.load()
        if not spot_name in deck_status:
            raise SpotNotFoundError(spot_name)
        return deck_status[spot_name]
    
    def get_all_spot_status(self):
        deck_status = self.load()
        return deck_status

    def put_item(self, spot_name, new_item):
        deck_status = self.load()
        if not spot_name in deck_status:
            raise SpotNotFoundError(spot_name)
        if not deck_status[spot_name] == None:
            raise OperationError(409, "Already item exists")

        deck_status[spot_name] = new_item
        print('========================================')
        print(deck_status)
        self.save(deck_status)
        return True

    def trash_item(self, spot_name):
        deck_status = self.load()
        if not spot_name in deck_status:
            raise SpotNotFoundError(spot_name)
        if deck_status[spot_name] == None:
            raise OperationError(code = 404, reason = "No object exists")
        deck_status[spot_name] = None
        self.save(deck_status)
        return True

    def move_item(self, from_spot_name, to_spot_name):
        deck_status = self.load()
        if not from_spot_name in deck_status:
            raise SpotNotFoundError(from_spot_name)
        if not to_spot_name in deck_status:
            raise SpotNotFoundError(to_spot_name)
        
        if deck_status[from_spot_name] == None:
            raise OperationError(404, "Item does not exist on {}".format(from_spot_name))
        if not deck_status[to_spot_name] == None:
            raise OperationError(409, "Item already exists on {}".format(to_spot_name))
        transfer_obj = deck_status[from_spot_name]
        deck_status[from_spot_name] = None
        deck_status[to_spot_name] = transfer_obj
        self.save(deck_status)
        return True

class ConsumablesManager:
    def __init__(self):
        self.consumables = {}

    def new_item(self, item_type: str, amount: int = 0):
        if item_type in self.consumables:
            raise OperationError(409, "Item already exists.")
        if amount < 0:
            raise OperationError(400, "Invalid number of amount")
        self.consumables[item_type] = {"amount": amount}
        return True

    def refill_item(self, item_type: str, amount: int):
        if not item_type in self.consumables:
            raise OperationError(404, "Item has not been registered.")
        if amount < 0:
            raise OperationError(400, "Invalid number of amount")
        self.consumables[item_type]["amount"] += amount
        return True
        
    def consume_item(self, item_type: str, amount: int):
        if not item_type in self.consumables:
            raise OperationError(404, "Item has not been registered.")
        if not amount < self.consumables[item_type]["amount"]:
            #XXX
            raise OperationError(400, "{} Not enough".format(item_type)) 
        self.consumables[item_type]["amount"] -= amount
    
    def status(self):
        ret = {item_type: value["amount"] for item_type, value in self.consumables.items()}
        return ret


if __name__ == '__main__':
    print("== Set up Deck: A-H spots")
    manager = DeckManager(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'])
    print(manager.get_all_spot_status())
    
    print("== Put item on spot A")
    manager.put_item(spot_name = 'A', new_item = {'uuid': 'hoge'})
    print(manager.get_all_spot_status())

    print("== Put item on spot C")
    manager.put_item(spot_name = 'C', new_item = {'uuid': 'aaa'})
    print(manager.get_all_spot_status())

    print("== Move item from A to H")
    manager.move_item("A", "H")
    print(manager.get_all_spot_status())

    print("== Try to move item from H to C (but will Fail!)")
    try:
        manager.move_item("H", "C")
    except OperationError as e:
        print(e.reason)
    print(manager.get_all_spot_status())

    print("****************************************")
    print("== Set up Consumables Manager")
    consumable_manager = ConsumablesManager()
    print(consumable_manager.status())

    print("== Set up water")
    consumable_manager.new_item("Water", 100)
    print(consumable_manager.status())

    print("== Set up 1 ml tip")
    consumable_manager.new_item("1ml Tip", 1000)
    print(consumable_manager.status())

    print("== Refill 10 ml of water")
    consumable_manager.refill_item("Water", 10)
    print(consumable_manager.status())

    print("== Use 40 ml of water")
    consumable_manager.consume_item("Water", 40)
    print(consumable_manager.status())

    print("== Use 80 ml of water")
    try:
        consumable_manager.consume_item("Water", 80)
    except OperationError as e:
        print(e.reason)
    print(consumable_manager.status())

