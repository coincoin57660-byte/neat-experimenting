import math
import json
import os


class Pendulum:
    def __init__(self,
            dt: float = 0.016, g: float = 9.81,
            m: float = 1.0, M: float = 5.0, l: float = 2.0
        ) -> None:

        self.dt = dt
        self.g = g  # gravité
        self.m = m  # masse pendule
        self.M = M  # masse chariot
        self.l = l  # longeur pendule

        self.max_x = 3
        self.max_force = 2

        self.logs = []

        self.reset(
            log = False
        )


    def reset(self, log: bool = False):# -> list[float]:

        self.x = 0.0
        self.x_dot = 0.0
        self.theta = math.pi
        self.theta_dot = 0.0
        self.max_angle = math.pi
        self.max_angle_inv = 0.0
        self.max_angle_inv_pour = 0.0
        self.total_angle_inv_pour = 0.0

        self.log = log

        if self.log:
            self.logs.append({
                'g': self.g,
                'm': self.m,
                'M': self.M,
                'l': self.l,
                'max_x': self.max_x
            })

            self.logs.append({
                't': 0,
                'x': self.x,
                'theta': self.theta,
                'x_dot': self.x_dot,
                'theta_dot': self.theta_dot,
                'force': 0.0
            })

        return self.get_state()


    def get_state(self):# -> list[float]:

        return [
            self.x / self.max_x,
            self.x_dot / 3,
            self.theta / math.pi,
            self.theta_dot / 4
        ]


    def step(self, action: list, t: int):# -> tuple[list[float], float, bool]:

        force = action[0]
        force *= self.max_force

        # calcul de l'accélération du chariot et du pendule
        sin_theta = math.sin(self.theta)
        cos_theta = math.cos(self.theta)
        total_mass = self.m - self.M

        # équations du pendule inversé
        theta_dd = (
            self.g * sin_theta + cos_theta * (
            -force - self.m * self.l * self.theta_dot ** 2 * sin_theta) / total_mass) / (
            self.l * (4.0 / 3.0 - self.m * cos_theta ** 2 / total_mass)
        )

        x_dd = (
            force + self.m * self.l * (
            self.theta_dot ** 2 * sin_theta - theta_dd * cos_theta)
        ) / total_mass

        # intégration Euler
        self.x_dot += x_dd * self.dt
        self.x += self.x_dot * self.dt

        self.theta_dot += theta_dd * self.dt
        self.theta += self.theta_dot * self.dt
        # ramène l'angle dans [-pi, pi]
        self.theta = (self.theta + math.pi) % (2 * math.pi) - math.pi

        # angle max
        self.max_angle = min(
            self.max_angle,
            abs(self.theta)
        )
        self.max_angle_inv = math.pi - abs(self.max_angle)
        self.max_angle_inv_pour = (self.max_angle_inv / math.pi) * 100
        self.total_angle_inv_pour += ((math.pi - abs(self.theta)) / math.pi) * 100


        # calcul de reward
        reward = (math.cos(self.theta) + 1) / 2

        if abs(self.x) > self.max_x:
            done = True
        else:
            done = False

        # save log
        if self.log:
            self.logs.append({
                't': t + 1,
                'x': self.x,
                'theta': self.theta,
                'x_dot': self.x_dot,
                'theta_dot': self.theta_dot,
                'force': force
            })

        return self.get_state(), reward, done


    def save_logs(self) -> None:

        base_dir = os.path.dirname(os.path.abspath(__file__))

        logs_dir = os.path.join(base_dir, 'logs')

        os.makedirs(logs_dir, exist_ok = True)

        filename = os.path.join(logs_dir, 'simulation.json')

        # sauvegard en JSON
        with open(filename, 'w') as f:

            json.dump(self.logs, f, indent = 4)