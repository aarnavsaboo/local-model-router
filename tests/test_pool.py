import unittest

from local_model_router.pool import ModelPool
from local_model_router.router import ModelProfile, Task
from local_model_router.scheduler import route
from local_model_router.simulation import replay


class Tests(unittest.TestCase):
    def test_memory_limit(self):
        pool = ModelPool([
            ModelProfile("a",4096,4,20,warm=True),
            ModelProfile("b",4096,8,20,warm=False),
        ], memory_limit_gb=10)
        self.assertFalse(pool.can_warm("b"))

    def test_route(self):
        pool = ModelPool([
            ModelProfile("a",8192,2,50,{"qa":.8},warm=True,capacity=2),
            ModelProfile("b",32768,8,20,{"qa":.9},warm=True),
        ])
        decision = route(pool, Task("qa",1000,100,min_quality=.75,id="x"))
        self.assertEqual(decision.model,"a")

    def test_simulation(self):
        pool = ModelPool([ModelProfile("a",8192,2,50,{"qa":1},warm=True,capacity=1)])
        rows = replay(pool,[
            Task("qa",100,100,id="1"),
            Task("qa",100,100,id="2"),
        ])
        self.assertEqual(len(rows),2)
        self.assertTrue(all(x["ok"] for x in rows))
        self.assertGreaterEqual(rows[1]["queued_s"],0)


if __name__=="__main__":
    unittest.main()
