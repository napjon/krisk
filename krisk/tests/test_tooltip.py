def test_tooltip(gap_chart):
    formatter = gap_chart.option["tooltip"]["formatter"]
    assert formatter == (
        "country: {@[4]}<br>lifeExp: {@[0]}<br>gdpPercap: {@[1]}<br>"
        "pop: {@[2]}<br>continent: {@[3]}<br>"
    )


def test_tooltip_rejects_executable_formatter(gap_chart):
    try:
        gap_chart.set_tooltip_format(["country"], formatter="() => 1")
    except ValueError as error:
        assert "Executable JavaScript" in str(error)
    else:
        raise AssertionError("Executable formatter was accepted")


def test_tooltip_style(decl_chart):
    template_tooltip = decl_chart.option["tooltip"]
    assert template_tooltip == {
        "axisPointer": {"type": "line"},
        "fontFamily": "sans-serif",
        "fontSize": 14,
        "fontStyle": "normal",
        "trigger": "item",
        "triggerOn": "mousemove",
    }

    decl_chart.set_tooltip_style(trigger="axis", axis_pointer="shadow", font_size=20)
    tooltip = decl_chart.option["tooltip"]
    assert tooltip == {
        "axisPointer": {"type": "shadow"},
        "fontFamily": "sans-serif",
        "fontSize": 20,
        "fontStyle": "normal",
        "trigger": "axis",
        "triggerOn": "mousemove",
    }
