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

        if self.cardinality > 500:
            for i, a in enumerate(self.gamestate):
                if self.gamestate[i].fluff:
                    self.active[i] = False

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

        return [
            serialized.cardinality,
            serialized.active.tolist(),
            serialized.canCollide.tolist(),
            serialized.p.tolist(),
            serialized.dp.tolist(),
            serialized.ddp.tolist(),
            serialized.mass.tolist(),
            serialized.theta.tolist(),
            serialized.dtheta.tolist(),
            serialized.ddtheta.tolist(),
            serialized.gamestate
        ]

    def deserialize(self, state, gamestateDeserializer):
        self.cardinality = state[0]
        self.active = np.array(state[1])
        self.canCollide = np.array(state[2])
        self.p = np.array(state[3])
        self.dp = np.array(state[4])
        self.ddp = np.array(state[5])
        self.mass = np.array(state[6])
        self.theta = np.array(state[7])
        self.dtheta = np.array(state[8])
        self.ddtheta = np.array(state[9])
        self.gamestate = map(gamestateDeserializer, state[10])

        self.dim = (self.cardinality, 2)

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
