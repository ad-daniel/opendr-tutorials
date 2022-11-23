from controller import Supervisor

robot = Supervisor()
timestep = int(robot.getBasicTimeStep())

root_node = robot.getRoot()
root_children_field = root_node.getField('children')

objects = ['BeerBottle', 'WaterBottle', 'Can', 'Book']
translations = [[-0.7, 0.5, 0.7], [-0.7, 0.5, 0.7], [-0.7, 0.5, 0.7], [-0.7, 0.5, 0.7]]

i = 0
j = 0
DURATION = 50
first_run = True
while robot.step(timestep) != -1:
    if i == 0:
        if not first_run:
            root_children_field.removeMF(-1)

        root_children_field.importMFNodeFromString(-1, f'{objects[j]} {{ translation {translations[j][0]} {translations[j][1]} {translations[j][2]} }}')
        first_run = False

    i = 0 if i == DURATION else i + 1
    j = 0 if j == len(objects) - 1 else j + 1
