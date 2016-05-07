from main import ViewPort

class UI:
    def __init__(self, game):
        self.vp = ViewPort()
        self.statusBar = StatusBar()
        self.game = game
        self.playerShip = game.getMobileController(0)

        self.menu = Menu(self)
        self.mode = 'game'
        self.quit = False
        self.turning = 0
        self.acceleration = 0
        self.lastKey = None

        self.isDecelerating = False
        self.isFiring = False

        self.playerWeapons = [
            [weapons.get('railgun')],
            [weapons.get('plasma')],
            [weapons.get('laser')]
        ]

        self.weaponIndex = 0

    def step(self, frame, tick):
        self.playerShip.turn(self.turning)
        self.playerShip.accel(self.acceleration)
        if self.isDecelerating:
            self.playerShip.decel()
        if self.isFiring:
            self.playerShip.fire(frame)

        # self.vp.step();
        self.vp.focus(self.game.objects.p[0][0], self.game.objects.p[0][1])

    def handleInputEvent(self, event):
        if self.mode == 'menu':
            self.mode = self.menu.actionPerformed(event)
            return None

        if event.type == KEYDOWN:
            if event.key == pg.K_ESCAPE:
                self.quit = True

            elif event.key == pg.K_BACKSPACE:
                self.playerShip.nextShip()

            elif event.key == pg.K_UP:
                self.acceleration = 1
                self.isDecelerating = False

            elif event.key == pg.K_DOWN:
                self.acceleration = -1
                self.isDecelerating = False

            elif event.key == pg.K_z:
                self.acceleration = 0
                self.isDecelerating = True

            elif event.key == pg.K_LEFT:
                self.turning = 1
                self.isDecelerating = False

            elif event.key == pg.K_RIGHT:
                self.turning = -1
                self.isDecelerating = False

            elif event.key == pg.K_h:
                self.playerShip.warpHome()

            elif event.key == pg.K_SPACE:
                self.isFiring = True

            elif event.key == pg.K_l:
                dock = self.game.dock()
                if dock is not None:
                    self.menu.show(dock)
                    self.mode = 'menu'

            elif event.key == pg.K_LEFTBRACKET:
                N = len(self.playerWeapons)
                self.weaponIndex = (N + self.weaponIndex - 1) % N
                self.game.objects.gamestate[0].weapons = self.playerWeapons[self.weaponIndex]

            elif event.key == pg.K_RIGHTBRACKET:
                self.weaponIndex = (self.weaponIndex + 1) % len(self.playerWeapons)
                self.game.objects.gamestate[0].weapons = self.playerWeapons[self.weaponIndex]

            elif event.key == pg.K_g:
                self.game.toggleGravity()

            elif event.key == pg.K_f:
                self.game.toggleFriction()

            # elif event.key == pg.K_t:
            #     self.playerShip.setTarget(self.game.getClosestShipToPlayer())

            self.lastKey = event.key


        elif event.type == KEYUP:
            if event.key == pg.K_UP:
                self.acceleration = 0
                self.isDecelerating = False

            elif event.key == pg.K_DOWN:
                self.acceleration = 0
                self.isDecelerating = False

            elif event.key == pg.K_LEFT:
                if self.lastKey != pg.K_RIGHT:
                    self.turning = 0

            elif event.key == pg.K_RIGHT:
                if self.lastKey != pg.K_LEFT:
                    self.turning = 0

            elif event.key == pg.K_SPACE:
                self.isFiring = False

            elif event.key == pg.K_z:
                self.acceleration = 0
                self.isDecelerating = False

            self.lastKey = event.key

        return None
