from sqlmodel import Session
from .models import Grids, Cells, Zones, CellsZonesLink, States, Users, Invites


main_grid = None

main_grid_cell_1 = None
main_grid_cell_2 = None
main_grid_cell_3 = None

main_grid_zone_1 = None
main_grid_zone_2 = None




other_grid = None

other_grid_cell_1 = None
other_grid_cell_2 = None
other_grid_cell_3 = None

other_grid_zone_1 = None
other_grid_zone_2 = None

other_grid_state = None

other_grid_cell_1_state = None
other_grid_cell_2_state = None
other_grid_cell_3_state = None

other_grid_zone_1_state = None
other_grid_zone_2_state = None


user_1 = None
user_2 = None
user_3 = None


def inject_users(session):
    global user_1, user_2, user_3
    user_1 = Users(name="Utilisateur", token="user1")
    user_2 = Users(name="Dev", token="user2")
    user_3 = Users(name="Admin", token="user3")
    users = [
        user_1,
        user_2,
        user_3
    ]
    for user in users:
        session.add(user)
    session.commit()
    for user in users:
        session.refresh(user)
    return users


def inject_grids(session):
    global main_grid, other_grid
    main_grid = Grids(name="Main grid", published=False, cells=[], owner_id=user_1.id)
    other_grid = Grids(name="Other grid", published=True, cells=[], owner_id=user_2.id)
    grids = [
        main_grid,
        other_grid
    ]
    for grid in grids:
        session.add(grid)
    session.commit()
    for grid in grids:
        session.refresh(grid)
    return grids


def inject_cells(session, grids):
    global main_grid_cell_1, main_grid_cell_2, main_grid_cell_3, other_grid_cell_1, other_grid_cell_2, other_grid_cell_3
    main_grid_cell_1 = Cells(name="Cell 1", position_x=0, position_y=0, points=21, grid_id=main_grid.id)
    main_grid_cell_2 = Cells(name="Cell 2", position_x=0, position_y=1, points=42, grid_id=main_grid.id)
    main_grid_cell_3 = Cells(name="Cell 3", position_x=0, position_y=2, points=84, grid_id=main_grid.id)
    other_grid_cell_1 = Cells(name="Other Cell 1", position_x=0, position_y=0, points=21, grid_id=other_grid.id)
    other_grid_cell_2 = Cells(name="Other Cell 2", position_x=0, position_y=1, points=42, grid_id=other_grid.id)
    other_grid_cell_3 = Cells(name="Other Cell 3", position_x=0, position_y=2, points=84, grid_id=other_grid.id)
    cells = [
        main_grid_cell_1,
        main_grid_cell_2,
        main_grid_cell_3,
        other_grid_cell_1,
        other_grid_cell_2,
        other_grid_cell_3
    ]
    for cell in cells:
        session.add(cell)
    session.commit()
    for cell in cells:
        session.refresh(cell)
    return cells


def inject_zones(session, grids, cells):
    global main_grid_zone_1, main_grid_zone_2, other_grid_zone_1, other_grid_zone_2
    main_grid_zone_1 = Zones(name="Zone 1", points=3, grid_id=main_grid.id, cells=[main_grid_cell_1, main_grid_cell_2])
    main_grid_zone_2 = Zones(name="Zone 2", points=3, grid_id=main_grid.id, cells=[main_grid_cell_2, main_grid_cell_3])
    other_grid_zone_1 = Zones(name="Other Zone 1", points=3, grid_id=other_grid.id, cells=[other_grid_cell_1, other_grid_cell_2])
    other_grid_zone_2 = Zones(name="Other Zone 2", points=3, grid_id=other_grid.id, cells=[other_grid_cell_2, other_grid_cell_3])
    zones = [
        main_grid_zone_1,
        main_grid_zone_2,
        other_grid_zone_1,
        other_grid_zone_2
    ]
    for zone in zones:
        session.add(zone)
    session.commit()
    for zone in zones:
        session.refresh(zone)
    return zones


def inject_states(session):
    global other_grid_state, other_grid_cell_1_state, other_grid_cell_2_state, other_grid_cell_3_state, other_grid_zone_1_state, other_grid_zone_2_state
    other_grid_state = States(user_id=user_1.id, status=False, marker="", entity_type="grid", entity_id=other_grid.id)

    other_grid_cell_1_state = States(user_id=user_1.id, status=False, marker="", entity_type="cell", entity_id=other_grid_cell_1.id)
    other_grid_cell_2_state = States(user_id=user_1.id, status=False, marker="", entity_type="cell", entity_id=other_grid_cell_2.id)
    other_grid_cell_3_state = States(user_id=user_1.id, status=False, marker="", entity_type="cell", entity_id=other_grid_cell_3.id)

    other_grid_zone_1_state = States(user_id=user_1.id, status=False, marker="", entity_type="zone", entity_id=other_grid_zone_1.id)
    other_grid_zone_2_state = States(user_id=user_1.id, status=False, marker="", entity_type="zone", entity_id=other_grid_zone_2.id)

    states = [
        other_grid_state,
        other_grid_cell_1_state,
        other_grid_cell_2_state,
        other_grid_cell_3_state,
        other_grid_zone_1_state,
        other_grid_zone_2_state
    ]
    for state in states:
        session.add(state)
    session.commit()
    return states


def inject_invites(session):
    invite_1 = Invites(desc="Invitation", grid_id=main_grid.id, author_id=user_1.id, guest_id=user_3.id)
    invite_2 = Invites(desc="Invitation", grid_id=main_grid.id, author_id=user_1.id, guest_id=user_2.id)
    invite_3 = Invites(desc="Invitation", grid_id=other_grid.id, author_id=user_2.id, guest_id=user_3.id)
    invites = [
        invite_1,
        invite_2,
        invite_3
    ]
    for invite in invites:
        session.add(invite)
    session.commit()
    return invites

def inject(engine):
    with Session(engine) as session:
        users = inject_users(session)
        grids = inject_grids(session)
        cells = inject_cells(session, grids)
        zones = inject_zones(session, grids, cells)
        states = inject_states(session)
        invites = inject_invites(session)
        session.close()
