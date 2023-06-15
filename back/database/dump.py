from sqlmodel import Session
from .models import Grids, Cells, Zones, States, Users, Invites


def inject_users(session):
	users = [
		Users(username="Utilisateur", password="user1"),
		Users(username="Dev", password="user2"),
		Users(username="Admin", password="user3", admin=True)
	]
	for user in users:
		session.add(user)
	session.commit()
	for user in users:
		session.refresh(user)
	return users


def inject_grids(session, users):
	grids = [
		Grids(name="Main grid", published=False, cells=[], owner_id=users[0].id),
		Grids(name="Other grid", published=True, cells=[], owner_id=users[1].id)
	]
	for grid in grids:
		session.add(grid)
	session.commit()
	for grid in grids:
		session.refresh(grid)
	return grids


def inject_cells(session, grids):
	cells = [
		Cells(name="Cell 2", position_x=0, position_y=1, points=42, grid_id=grids[0].id),
		Cells(name="Cell 1", position_x=0, position_y=0, points=21, grid_id=grids[0].id),
		Cells(name="Cell 3", position_x=0, position_y=2, points=84, grid_id=grids[0].id),
		Cells(name="Other Cell 1", position_x=0, position_y=0, points=21, grid_id=grids[1].id),
		Cells(name="Other Cell 2", position_x=0, position_y=1, points=42, grid_id=grids[1].id),
		Cells(name="Other Cell 3", position_x=0, position_y=2, points=84, grid_id=grids[1].id)
	]
	for cell in cells:
		session.add(cell)
	session.commit()
	for cell in cells:
		session.refresh(cell)
	return cells


def inject_zones(session, grids, cells):
	zones = [
		Zones(name="Zone 1", points=3, grid_id=grids[0].id, cells=[cells[0], cells[1]]),
		Zones(name="Zone 2", points=3, grid_id=grids[0].id, cells=[cells[1], cells[2]]),
		Zones(name="Other Zone 1", points=3, grid_id=grids[1].id, cells=[cells[3], cells[4]]),
		Zones(name="Other Zone 2", points=3, grid_id=grids[1].id, cells=[cells[4], cells[5]])
	]
	for zone in zones:
		session.add(zone)
	session.commit()
	for zone in zones:
		session.refresh(zone)
	return zones


def inject_states(session, users, grids, cells, zones):
	states = [
		States(user_id=users[0].id, status=False, marker="", entity_type="grid", entity_id=grids[1].id),
		States(user_id=users[0].id, status=False, marker="", entity_type="cell", entity_id=cells[3].id),
		States(user_id=users[0].id, status=False, marker="", entity_type="cell", entity_id=cells[4].id),
		States(user_id=users[0].id, status=False, marker="", entity_type="cell", entity_id=cells[5].id),
		States(user_id=users[0].id, status=False, marker="", entity_type="zone", entity_id=zones[2].id),
		States(user_id=users[0].id, status=False, marker="", entity_type="zone", entity_id=zones[3].id)

	]
	for state in states:
		session.add(state)
	session.commit()
	return states


def inject_invites(session, users, grids):

	invites = [
		Invites(desc="Invitation", grid_id=grids[0].id, author_id=users[0].id, guest_id=users[2].id),
		Invites(desc="Invitation", grid_id=grids[0].id, author_id=users[0].id, guest_id=users[1].id),
		Invites(desc="Invitation", grid_id=grids[1].id, author_id=users[1].id, guest_id=users[2].id)
	]
	for invite in invites:
		session.add(invite)
	session.commit()
	return invites

def inject(engine):
	with Session(engine) as session:
		users = inject_users(session)
		grids = inject_grids(session, users)
		cells = inject_cells(session, grids)
		zones = inject_zones(session, grids, cells)
		inject_states(session, users, grids, cells, zones)
		inject_invites(session, users, grids)
		session.close()
