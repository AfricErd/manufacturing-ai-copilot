from runtime.planner import Planner


def test_planner_is_abstract():
    try:
        Planner()
        assert False
    except TypeError:
        assert True