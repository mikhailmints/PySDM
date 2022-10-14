# pylint: disable=missing-module-docstring,missing-class-docstring,missing-function-docstring
import numpy as np

from PySDM import Builder
from PySDM.backends import CPU
from PySDM.dynamics import Condensation
from PySDM.environments import Box


class TestBuilder:
    @staticmethod
    def test_build_minimal():
        # arrange
        builder = Builder(backend=CPU(), n_sd=1)
        builder.set_environment(Box(dt=np.nan, dv=np.nan))

        # act
        particulator = builder.build(
            products=(), attributes={k: np.asarray([0]) for k in ("n", "volume")}
        )

        # assert
        _ = particulator.attributes

    @staticmethod
    def test_request_attribute():
        # arrange
        env = Box(dt=-1, dv=np.nan)
        builder = Builder(backend=CPU(), n_sd=1)
        builder.set_environment(env)
        builder.add_dynamic(Condensation())

        # act
        builder.request_attribute("critical supersaturation")

        # assert
        particulator = builder.build(
            products=(),
            attributes={
                k: np.asarray([0])
                for k in ("n", "volume", "dry volume", "kappa times dry volume")
            },
        )
        env["T"] = np.nan
        _ = particulator.attributes["critical supersaturation"].to_ndarray()
