import math
import numpy as np
import numpy.linalg as LA

class PatrolPlanets:
    def __init__(self, controller):
        self.controller = controller

class StopAtDestination:
    def __init__(self, controller, target):
        self.controller = controller
        self.target = target
        self.stopping = False
        self.stoppingDistance = self.calculateStoppingDistance()
        print "My stopping distance is %f." % self.stoppingDistance

    def calculateStoppingDistance(self):
        v = self.controller.objects.dp[self.controller.index]
        ship = self.controller.objects.gamestate[self.controller.index]
        a = ship.thrust / ship.mass
        s = LA.norm(v)
        s2 = s * s
        return abs(0.5 * (0 - s2) / a)

    def step(self):
        i = self.controller.index
        o = self.controller.objects
        v = o.dp[i]

        aheadness = np.dot(v, self.target - o.p[i])
        stillAhead = aheadness > 0
        distance = LA.norm(self.target - o.p[i])

        if not self.stopping:
            if not stillAhead or distance < self.stoppingDistance * 1.1:
                self.stopping = True
            return True

        speed = LA.norm(v)

        if speed < 20:
            o.dp[i] = (0, 0)
            print 'Destination reached. Giving up the ghost.'
            self.controller.off()
            return False

        self.controller.decel()
        return True # stay alive

class FaceTarget:
    def __init__(self, controller, target):
        self.controller = controller
        self.target = target

    def step(self):
        i = self.controller.index
        j = self.target.index
        o = self.controller.objects

        dp = o.p[j] - o.p[i]

        angleToTarget = 180 * math.atan2(-dp[1], dp[0]) / math.pi

        self.controller.turnTo(angleToTarget)
        return True

class FollowTarget:
    def __init__(self, controller, target):
        self.controller = controller
        self.target = target
        self.turning = False
        self.thrusting = False

    def step(self):
        i = self.controller.index
        j = self.target.index
        o = self.controller.objects

        maxThrust = o.gamestate[i].thrust / o.gamestate[i].mass


        targetPoint = o.p[j] - o.p[i]
        angleToTarget = (180 * math.atan2(-targetPoint[1], targetPoint[0]) / math.pi) % 360
        theta0 = o.theta[i] % 360
        diff = theta0 - angleToTarget
        adiff = abs(diff)
        if adiff > 40:
            # print 'correcting angle to %f (%f)' % (angleToTarget, diff)
            self.controller.turnTo(angleToTarget)
        elif adiff > 20:
            # print 'fine-tuning angle to %f (%f)' % (angleToTarget, diff)
            self.controller.turnTo(angleToTarget, 0.5)
        elif adiff > 10:
            # print 'fine-tuning angle to %f (%f)' % (angleToTarget, diff)
            self.controller.turnTo(angleToTarget, 0.1)
        else:
            self.controller.turn(0)


        rp = o.p[i] - o.p[j]
        rv = o.dp[i] - o.dp[j]
        distance = LA.norm(rp)
        if distance > 200:
            o.ddp[i] = -0.2 * rp - 0.5 * rv + 0.1 * o.ddp[j]
            # print 'closing'
        elif distance < 50:
            o.ddp[i] = 0.5 * rp - 0.5 * rv
            # print 'backing off'
        else:
            o.ddp[i] = -0.9 * rv
            # print 'killing relative velocity'

        a = LA.norm(o.ddp[i])
        if a > maxThrust:
            o.ddp[i] *= maxThrust / a

        return True

class EnemyNN:
    def __init__(self, mobileController, target):
        self.mobileController = mobileController
        self.objects = mobileController.objects
        self.index = mobileController.index
        self.target = target

        self.hiddenLayer = 0.1 * (np.random.random((10, 18)) - 0.5)
        self.hiddenLayer2 = 0.1 * (np.random.random((6, 10)) - 0.5)
        # fire, accel, decel, turnleft, turnright
        self.previousOutputs = np.zeros(6)

    def step(self, frame):
        i = self.index
        o = self.objects
        t = self.target
        a = [
            o.p[i][0], o.p[i][1], o.dp[i][0], o.dp[i][1], o.theta[i], o.dtheta[i],
            o.p[t][0], o.p[t][1], o.dp[t][0], o.dp[t][1], o.theta[t], o.dtheta[t],
        ]
        a.extend(self.previousOutputs)
        inputs = np.array(a)
        r = np.dot(self.hiddenLayer, inputs) > 0
        r = np.dot(self.hiddenLayer2, r) > 0
        actions = [
            lambda: self.mobileController.fire(frame),
            lambda: self.mobileController.accel(-1),
            lambda: self.mobileController.accel(1),
            lambda: self.mobileController.decel(),
            lambda: self.mobileController.turn(-1),
            lambda: self.mobileController.turn(1)
        ]
        for i, v in enumerate(r):
            if v:
                actions[i]()
