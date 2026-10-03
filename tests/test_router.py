import unittest
from local_model_router import ModelProfile, Task, Observation, choose, update_profile


class RouterTests(unittest.TestCase):
    def test_picks_fast_feasible_model(self):
        models = [
            ModelProfile("small", 8192, 2, 50, {"qa": .8}, warm=True),
            ModelProfile("large", 32768, 8, 20, {"qa": .9}, warm=True),
        ]
        self.assertEqual(choose(models, Task("qa", 1000, 200, min_quality=.75)).name, "small")

    def test_context_can_force_larger_model(self):
        models = [
            ModelProfile("small", 2048, 2, 50, {"qa": .8}),
            ModelProfile("large", 32768, 8, 20, {"qa": .9}),
        ]
        self.assertEqual(choose(models, Task("qa", 5000, 200)).name, "large")

    def test_update_uses_ewma(self):
        model = ModelProfile("m", 4096, 2, 20)
        out = update_profile(model, Observation(2, 100, True), alpha=.5)
        self.assertEqual(out.tps, 35)
        self.assertTrue(out.warm)


if __name__ == "__main__":
    unittest.main()
