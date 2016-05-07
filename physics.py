import numpy as np
import copy

class IndexRef:
    def __init__(self, index):
        self.index = index

class PhysicalObjects:
    def __init__(self, n, gamestateConstructor):
        self.references = {}

        if n == 0:
            self.cardinality = 0
            self.gamestateConstructor = gamestateConstructor
            self.dim = None

            self.active = None
            self.canCollide = None

            self.p = None
            self.dp = None
            self.ddp = None
            self.mass = None
            self.theta = None
            self.dtheta = None
            self.ddtheta = None
            self.gamestate = None
        else:
            self.gamestateConstructor = gamestateConstructor
            self.cardinality = n
            self.dim = (n, 2)
            self.active = np.ones(self.cardinality, dtype=np.bool)
            self.canCollide = np.zeros(self.cardinality, dtype=np.bool)
            self.p = np.zeros(self.dim)
            self.dp = np.zeros(self.dim)
            self.ddp = np.zeros(self.dim)
            self.mass = np.ones(n)
            self.theta = np.zeros(n)
            self.dtheta = np.zeros(n)
            self.ddtheta = np.zeros(n)
            self.gamestate = [gamestateConstructor() for i in xrange(n)]

    def add(self, k, gamestateConstructor):
        if gamestateConstructor is None:
            gamestateConstructor = self.gamestateConstructor
        firstNew = self.cardinality
        self.cardinality += k
        self.dim = (self.cardinality, 2)
        self.active.resize(self.cardinality)
        self.active[firstNew:firstNew+k] = True
        self.canCollide.resize(self.cardinality)
        self.p.resize(self.dim, refcheck=False)
        self.dp.resize(self.dim, refcheck=False)
        self.ddp.resize(self.dim, refcheck=False)
        self.mass.resize(self.cardinality, refcheck=False)
        self.theta.resize(self.cardinality, refcheck=False)
        self.dtheta.resize(self.cardinality, refcheck=False)
        self.ddtheta.resize(self.cardinality, refcheck=False)
        while len(self.gamestate) < self.cardinality:
            self.gamestate.append(gamestateConstructor())
        return firstNew

    def activate(self, i):
        self.active[i] = True

    def compact(self):
        before = self.active.shape[0]

        newGamestate = []
        indexOffset = 0
        for i, a in enumerate(self.active):
            if i in self.references:
                ref = self.references[i]
                del self.references[i]
                ref.index -= indexOffset
                self.references[ref.index] = ref
            if a:
                newGamestate.append(self.gamestate[i])
            else:
                indexOffset += 1

        self.gamestate = newGamestate
        self.canCollide = np.compress(self.active, self.canCollide, axis=0)

        self.p = np.compress(self.active, self.p, axis=0)
        self.dp = np.compress(self.active, self.dp, axis=0)
        self.ddp = np.compress(self.active, self.ddp, axis=0)
        self.mass = np.compress(self.active, self.mass, axis=0)
        self.theta = np.compress(self.active, self.theta, axis=0)
        self.dtheta = np.compress(self.active, self.dtheta, axis=0)
        self.ddtheta = np.compress(self.active, self.ddtheta, axis=0)
        self.active = np.compress(self.active, self.active, axis=0)
        self.cardinality = self.active.shape[0]
        self.dim = (self.cardinality, 2)
        return before - self.cardinality

    def ref(self, i):
        r = IndexRef(i)
        self.references[i] = r
        return r

    def releaseRef(self, ref):
        del self.references[ref.index]

    def serialize(self):
        serialized = copy.copy(self)
        serialized.gamestate = map(lambda s: s.serialize(), serialized.gamestate)
        for i in xrange(serialized.cardinality):
            if serialized.gamestate[i] is None:
                serialized.active[i] = False
        serialized.compact()

        serialized.p = map(list, serialized.p)
        serialized.dp = map(list, serialized.dp)
        serialized.ddp = map(list, serialized.ddp)
        serialized.mass = map(float, serialized.mass)
        serialized.theta = map(float, serialized.theta)
        serialized.dtheta = map(float, serialized.dtheta)
        serialized.ddtheta = map(float, serialized.ddtheta)
        serialized.active = map(bool, serialized.active)
        serialized.canCollide = map(bool, serialized.canCollide)
        return serialized

    def deserialize(self, gamestateDeserializer):
        self.gamestate = map(gamestateDeserializer, self.gamestate)
        self.p = np.array(self.p)
        self.dp = np.array(self.dp)
        self.ddp = np.array(self.ddp)
        self.mass = np.array(self.mass)
        self.theta = np.array(self.theta)
        self.dtheta = np.array(self.dtheta)
        self.ddtheta = np.array(self.ddtheta)
        self.active = np.array(self.active)
        self.canCollide = np.array(self.canCollide)
        return self

class FixedPhysicalObjects:
    def __init__(self, n, gamestateConstructor = None):
        self.cardinality = n
        self.dim = (n, 2)
        self.p = np.zeros(self.dim)
        self.mass = np.ones(n)
        self.theta = np.zeros(n)
        self.gamestate = [gamestateConstructor() for i in xrange(n)]

    def serialize(self):
        serialized = copy.copy(self)
        serialized.gamestate = map(lambda s: s.serialize(), serialized.gamestate)
        return serialized
