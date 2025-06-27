from manager import DeckManager, SpotNotFoundError, OperationError, ConsumablesManager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uuid

app = FastAPI()
manager = DeckManager(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'], "deck_state.yaml")
consumables_manager = ConsumablesManager()

class MoveRequest(BaseModel):
    from_spot: str
    to_spot: str

@app.post("/move")
def move_item(req: MoveRequest):
    try:
        manager.move_item(req.from_spot, req.to_spot)
        return {"status": "ok"}
    except SpotNotFoundError as e:
        raise HTTPException("move error")

class Item(BaseModel):
    uuid: uuid.UUID
    item_type: str

@app.put("/put_item/{spot_name}/")
def put_item(spot_name: str, item: Item):
    print("put_item", spot_name, item.model_dump(mode = 'json'))
    try:
        manager.put_item(spot_name, item.model_dump(mode = 'json'))
        return {"status": "ok"}
    except OperationError as e:
        raise HTTPException(status_code = e.code)

@app.delete("/delete/{spot_name}")
def trash_item(spot_name: str):
    try:
        ret = manager.trash_item(spot_name)
        if ret == True:
            return {"status": "ok"}
        else:
            raise HTTPException(status_code=404, detail = str(f"No item in {spot_name}"))
    except SpotNotFoundError as e:
        raise HTTPException(status_code = 404, detail = str(f"Spot {spot_name} not found"))

@app.get("/state")
def get_state():
    return manager.get_all_spot_status()

class ConsumableItem(BaseModel):
    item_type: str
    amount: int = 0

@app.post("/new_consumable")
def new_consumable(item: ConsumableItem):
    try:
        consumables_manager.new_item(item.item_type, item.amount)
    except OperationError as e:
        if e.code == 409 or e.code == 400:
            raise HTTPException(e.code, e.reason)
    return True

@app.patch("/refill/")
def refill_consumable(item: ConsumableItem):
    try:
        consumables_manager.refill_item(item.item_type, item.amount)
    except OperationError as e:
        if e.code == 404 or e.code == 400:
            raise HTTPException(e.code, e.reason)
    return True

@app.patch("/use/")
def use_consumable(item: ConsumableItem):
    try:
        consumables_manager.consume_item(item.item_type, item.amount)
    except OperationError as e:
        if e.code == 404 or e.code == 400:
            raise HTTPException(e.code, e.reason)
    return True

@app.get("/consumables_state")
def get_consumables_state():
    return consumables_manager.status()