def test_smoke_imports():
    import p3_tools
    import security_utils

    assert hasattr(p3_tools, "analyze_project_request")
    assert hasattr(security_utils, "validate_user_input")
