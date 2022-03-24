import numpy as np


class Grid:

    def __init__(self, n=20, m=20, x_range=(-10, 10), y_range=(-10, 10)):
        self.n, self.m = n, m
        self.x_range, self.y_range = x_range, y_range
        self.x, self.y = self.generate_grid()

    def generate_grid(self):
        return np.meshgrid(np.linspace(self.x_range[0], self.x_range[1], self.m), np.linspace(self.y_range[0], self.y_range[1], self.n))


class SpinLattice:

    def __init__(self, grid=None, grid_args={}):
        self.grid = grid if grid else Grid(**grid_args)
        self.angle = self.generate_random_angles()
        self.x, self.y = self.generate_spin_lattice()

    def generate_random_angles(self):
        return np.random.rand(self.grid.n, self.grid.m) * 2 * np.pi

    def generate_spin_lattice(self):
        return np.sin(self.angle), np.cos(self.angle)

    def update_spins(self, x, y):
        self.x, self.y = x, y

    def calculate_sum_of_neighboring_spins(self):
        x_neighbors = np.c_[self.x[:, 1:], np.zeros((self.grid.n, 1))] \
            + np.c_[np.zeros((self.grid.n, 1)), self.x[:, :-1]] \
            + np.r_[self.x[1:, :], np.zeros((1, self.grid.m))] \
            + np.r_[np.zeros((1, self.grid.m)), self.x[:-1, :]] \

        y_neighbors = np.c_[self.y[:, 1:], np.zeros((self.grid.n, 1))] \
            + np.c_[np.zeros((self.grid.n, 1)), self.y[:, :-1]] \
            + np.r_[self.y[1:, :], np.zeros((1, self.grid.m))] \
            + np.r_[np.zeros((1, self.grid.m)), self.y[:-1, :]] \
    
        return x_neighbors, y_neighbors

    def rotate_spins(self, theta):
        self.x = np.cos(theta) * self.x + np.sin(theta) * self.y
        self.y = -np.sin(theta) * self.x + np.cos(theta) * self.y
    
    def reset(self):
        self.angle = self.generate_random_angles()
        self.x, self.y = self.generate_spin_lattice()


class Field:

    def __init__(self, field_type='uniform', grid=None, grid_args={}):
        self.grid = grid if grid else Grid(**grid_args)
        self.field_type = field_type
        self.x, self.y = self.generate_field()

    def generate_field(self):
        if self.field_type == 'increasing curl':
            return -.25*self.grid.y, .25*self.grid.x
        if self.field_type == 'decreasing curl':
            return -4*self.grid.y / (self.grid.x**2 + self.grid.y**2), 4*self.grid.x / (self.grid.x**2 + self.grid.y**2)
        if self.field_type == 'curl':
            return -self.grid.y / np.sqrt(self.grid.x**2 + self.grid.y**2), self.grid.x / np.sqrt(self.grid.x**2 + self.grid.y**2)
        if self.field_type == 'increasing radial':
            return .25*self.grid.x, .25*self.grid.y
        if self.field_type == 'decreasing radial':
            return 4*self.grid.x / (self.grid.x**2 + self.grid.y**2), 4*self.grid.y / (self.grid.x**2 + self.grid.y**2)
        if self.field_type == 'radial':
            return self.grid.x / np.sqrt(self.grid.x**2 + self.grid.y**2), self.grid.y / np.sqrt(self.grid.x**2 + self.grid.y**2)
        if self.field_type == 'uniform':
            return np.ones(self.grid.x.shape), np.ones(self.grid.y.shape)

    def change_type(self, field_type):
        self.field_type = field_type


class SpinLatticeWithField:

    def __init__(self, field_coefficient=1, spin_coefficient=1, grid=None, grid_args={}, spin_lattice_args={}, field_args={}):
        self.field_coefficient = field_coefficient
        self.spin_coefficient = spin_coefficient
        self.grid = grid if grid else Grid(**grid_args)
        self.spin_lattice = SpinLattice(**spin_lattice_args, grid=grid)
        self.field = Field(**field_args, grid=grid)

    def calculate_force(self):
        x_neighbors, y_neighbors = self.spin_lattice.calculate_sum_of_neighboring_spins()
        x_force = self.field_coefficient * self.field.x + self.spin_coefficient * x_neighbors
        y_force = self.field_coefficient * self.field.y + self.spin_coefficient * y_neighbors
        return x_force, y_force

    def calculate_angular_momentum(self):
        x_force, y_force = self.calculate_force()
        return self.spin_lattice.x*y_force - self.spin_lattice.y*x_force

    def rotate_spins(self, theta):
        self.spin_lattice.rotate_spins(theta)

    def incrementally_rotate_spins_according_to_force(self, increment, n_increments):
        for _ in range(n_increments):
            theta = increment * self.calculate_angular_momentum()
            self.rotate_spins(theta)

    def reset_spin_lattice(self):
        self.spin_lattice.reset()

    def change_field_type(self, field_type):
        self.field.change_type(field_type)
