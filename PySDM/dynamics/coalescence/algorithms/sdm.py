"""
Created at 07.06.2019

@author: Piotr Bartman
@author: Sylwester Arabas
"""

from PySDM.particles_builder import ParticlesBuilder


class SDM:

    def __init__(self, particles_builder: ParticlesBuilder, kernel, seed=None):
        self.particles = particles_builder.particles

        kernel.register(particles_builder)
        self.kernel = kernel

        self.temp = self.particles.backend.IndexedStorage.empty(self.particles.n_sd, dtype=float)
        self.rand = self.particles.backend.Storage.empty(self.particles.n_sd // 2, dtype=float)
        self.prob = self.particles.backend.IndexedStorage.empty(self.particles.n_sd, dtype=float)
        self.is_first_in_pair = self.particles.backend.IndexedStorage.empty(self.particles.n_sd, dtype=int)  # TODO bool
        self.rnd = self.particles.backend.Random(self.particles.n_sd, seed)

        self.enable = True

    def __call__(self):
        if self.enable:
            self.particles.state.sanitize()

            self.temp.urand(self.rnd)

            self.toss_pairs(self.is_first_in_pair, self.temp)

            self.compute_probability(self.prob, self.temp, self.is_first_in_pair)

            self.rand.urand(self.rnd)
            self.compute_gamma(self.prob, self.rand)

            self.particles.coalescence(gamma=self.prob)

    def compute_gamma(self, prob, rand):
        self.particles.backend.compute_gamma(prob, rand)

    def compute_probability(self, prob, temp, is_first_in_pair):
        kernel_temp = temp
        self.kernel(kernel_temp, is_first_in_pair)
        self.particles.max_pair(prob, is_first_in_pair)
        prob *= kernel_temp

        norm_factor = temp
        self.particles.normalize(prob, norm_factor)

    def toss_pairs(self, is_first_in_pair, u01):
        self.particles.permute(u01)
        self.particles.find_pairs(is_first_in_pair)


