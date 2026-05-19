from scripts.verify_unimoral_task_builders import verify_task_builders


def test_unimoral_task_builder_verifier_passes_with_fixture():
    assert verify_task_builders() == []
