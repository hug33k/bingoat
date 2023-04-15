from sqlmodel import Session
from .models import Grids, Cells, Zones, CellsZonesLink, States


def inject_grids(session):
    grids = [
        Grids(name="My first grid", cells=[]),
        Grids(name="My other grid", cells=[]),
    ]
    for grid in grids:
        session.add(grid)
    session.commit()
    return grids


def inject_cells(session, grids):
    cells = [
        Cells(name="My first cell", position_x=0, position_y=0, points=420, grid_id=grids[0].id),
        Cells(name="My other cell", position_x=1, position_y=1, points=69, grid_id=grids[0].id),
    ]
    for cell in cells:
        session.add(cell)
    session.commit()
    return cells


def inject_zones(session, grids, cells):
    zones = [
        Zones(name="My first zone", points=42, grid_id=grids[0].id, cells=cells),
        Zones(name="My other zone", points=609, grid_id=grids[0].id, cells=[cells[0]]),
    ]
    for zone in zones:
        session.add(zone)
    session.commit()
    return zones


def inject_states(session):
    states = [
        States(user="test", status=False, marker="", entity_type="grid", entity_id=1),
        States(user="test", status=True, marker="blblbl", entity_type="cell", entity_id=1)
    ]
    for state in states:
        session.add(state)
    session.commit()
    return states


def inject(engine):
    with Session(engine) as session:
        grids = inject_grids(session)
        cells = inject_cells(session, grids)
        zones = inject_zones(session, grids, cells)
        states = inject_states(session)
        session.close()
