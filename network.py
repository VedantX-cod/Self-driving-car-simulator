import numpy as np
import copy


class NeuralNetwork:
    def __init__(self, sizes=(5, 8, 2)):
        self.sizes = sizes
        self.w1 = np.random.uniform(-1, 1, (sizes[0], sizes[1]))
        self.b1 = np.random.uniform(-1, 1, sizes[1])
        self.w2 = np.random.uniform(-1, 1, (sizes[1], sizes[2]))
        self.b2 = np.random.uniform(-1, 1, sizes[2])

    def forward(self, inputs):
        hidden = np.tanh(np.dot(inputs, self.w1) + self.b1)
        return np.tanh(np.dot(hidden, self.w2) + self.b2)

    def copy(self):
        return copy.deepcopy(self)

    def mutate(self, rate=0.1, strength=0.3):
        for arr in (self.w1, self.b1, self.w2, self.b2):
            mask = np.random.rand(*arr.shape) < rate
            arr += mask * np.random.normal(0, strength, arr.shape)

    @staticmethod
    def crossover(a, b):
        child = a.copy()
        for name in ("w1", "b1", "w2", "b2"):
            pa, pb = getattr(a, name), getattr(b, name)
            mask = np.random.rand(*pa.shape) < 0.5
            setattr(child, name, np.where(mask, pa, pb))
        return child

    def save(self, path="best_brain.npz"):
        np.savez(path, w1=self.w1, b1=self.b1, w2=self.w2, b2=self.b2)

    @staticmethod
    def load(path="best_brain.npz"):
        data = np.load(path)
        net = NeuralNetwork()
        net.w1, net.b1 = data["w1"], data["b1"]
        net.w2, net.b2 = data["w2"], data["b2"]
        return net